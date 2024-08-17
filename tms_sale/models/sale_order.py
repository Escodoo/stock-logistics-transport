# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    tms_order_ids = fields.Many2many(
        "tms.order",
        compute="_compute_tms_order_ids",
        string="TMS orders associated to this sale",
    )
    tms_order_count = fields.Integer(
        string="TMS Orders", compute="_compute_tms_order_ids"
    )

    has_tms_product = fields.Boolean(compute="_compute_has_tms_product")

    tms_route_flag = fields.Boolean(string="Use Routes")
    tms_route_id = fields.Many2one("tms.route", string="Routes")
    tms_origin_id = fields.Many2one(
        "res.partner", string="Origin", domain="[('tms_type', '=', 'location')]"
    )
    tms_destination_id = fields.Many2one(
        "res.partner", string="Destination", domain="[('tms_type', '=', 'location')]"
    )

    tms_scheduled_date_start = fields.Datetime(
        string="Scheduled Start", default=fields.Datetime.now
    )
    tms_scheduled_date_end = fields.Datetime(string="Scheduled End")
    tms_scheduled_duration = fields.Float(string="Scheduled Duration")

    @api.onchange("tms_route_flag")
    def _onchange_tms_route_flag(self):
        if self.tms_route_flag:
            self.tms_origin_id = None
            self.tms_destination_id = None
        else:
            self.tms_route_id = None

    @api.onchange("tms_route_id")
    def _onchange_tms_route_id(self):
        if self.tms_route_flag:
            if self.tms_route_id.estimated_time_uom.name == "Days":
                self.tms_scheduled_duration = self.tms_route_id.estimated_time * 24
            else:
                self.tms_scheduled_duration = self.tms_route_id.estimated_time
        else:
            self.tms_scheduled_duration = 0.0

    @api.onchange("tms_scheduled_duration")
    def _onchange_tms_scheduled_duration(self):
        if self.tms_scheduled_date_start and self.tms_scheduled_duration:
            self.tms_scheduled_date_end = self.tms_scheduled_date_start + timedelta(
                hours=self.tms_scheduled_duration
            )

    @api.onchange("tms_scheduled_date_end")
    def _onchange_tms_scheduled_date_end(self):
        if self.tms_scheduled_date_end and self.tms_scheduled_date_start:
            difference = self.tms_scheduled_date_end - self.tms_scheduled_date_start
            self.tms_scheduled_duration = difference.total_seconds() / 3600

    @api.onchange("tms_scheduled_date_start")
    def _onchange_tms_scheduled_date_start(self):
        if self.tms_scheduled_date_start:
            # Se a data de fim estiver vazia e houver duração, calcula a data de fim
            if self.tms_scheduled_duration and not self.tms_scheduled_date_end:
                self.tms_scheduled_date_end = self.tms_scheduled_date_start + timedelta(
                    hours=self.tms_scheduled_duration
                )
            # Se a data de fim estiver preenchida, ajusta conforme a duração
            elif self.tms_scheduled_date_end:
                self.tms_scheduled_date_end = self.tms_scheduled_date_start + timedelta(
                    hours=self.tms_scheduled_duration
                )

    @api.depends("order_line")
    def _compute_has_tms_product(self):
        for sale in self:
            has_tms_product = any(
                line.product_template_id.tms_product for line in sale.order_line
            )
            sale.has_tms_product = has_tms_product

    @api.depends("order_line")
    def _compute_tms_order_ids(self):
        for sale in self:
            tms = self.env["tms.order"].search(
                [
                    "|",
                    ("sale_id", "=", sale.id),
                    ("sale_line_id", "in", sale.order_line.ids),
                ]
            )
            sale.tms_order_ids = tms
            sale.tms_order_count = len(sale.tms_order_ids)

    def _prepare_line_tms_values(self, line):
        """
        Prepare the values to create a new TMS Order from a sale order line.
        """
        self.ensure_one()
        vals = self._prepare_tms_values(so_id=self.id, sol_id=line.id)
        return vals

    def _prepare_tms_values(self, **kwargs):
        """
        Prepare the values to create a new TMS Order from a sale order.
        """
        self.ensure_one()
        return {
            "sale_id": kwargs.get("so_id", False),
            "sale_line_id": kwargs.get("sol_id", False),
            "company_id": self.company_id.id,
            "partner_id": self.partner_id.id,
            "route": self.tms_route_flag,
            "route_id": self.tms_route_id.id or None,
            "origin_id": self.tms_origin_id.id or None,
            "destination_id": self.tms_destination_id.id or None,
            "scheduled_date_start": self.tms_scheduled_date_start or None,
            "scheduled_date_end": self.tms_scheduled_date_end or None,
        }

    def _tms_generate_sale_tms_orders(self, new_tms_sol):
        """
        Generate the TMS Order for this sale order if it doesn't exist.
        """
        self.ensure_one()
        new_tms_orders = self.env["tms.order"]

        if new_tms_sol:
            tms_by_sale = self.env["tms.order"].search(
                [("sale_id", "=", self.id), ("sale_line_id", "=", False)]
            )
            if not tms_by_sale:
                vals = self._prepare_tms_values(so_id=self.id)
                tms_by_sale = self.env["tms.order"].sudo().create(vals)
                new_tms_orders |= tms_by_sale
            new_tms_sol.write({"tms_order_id": tms_by_sale.id})

        return new_tms_orders

    def _tms_generate_line_tms_orders(self, new_tms_sol):
        """
        Generate TMS Orders for the given sale order lines.

        Override this method to filter lines to generate TMS Orders for.
        """
        self.ensure_one()
        new_tms_orders = self.env["tms.order"]

        for line in new_tms_sol:
            vals = self._prepare_line_tms_values(line)
            tms_by_line = self.env["tms.order"].sudo().create(vals)
            line.write({"tms_order_id": tms_by_line.id})
            new_tms_orders |= tms_by_line

        return new_tms_orders

    def _tms_generate(self):
        """
        Generate TMS Orders for this sale order.

        Override this method to add new tms_tracking types.
        """
        self.ensure_one()
        if not self.tms_order_ids:
            new_tms_orders = self.env["tms.order"]

            # Process lines set to TMS Sale
            new_tms_sale_sol = self.order_line.filtered(
                lambda L: L.product_id.tms_tracking == "sale" and not L.tms_order_id
            )
            new_tms_orders |= self._tms_generate_sale_tms_orders(new_tms_sale_sol)

            # Create new TMS Order for lines set to TMS Sale
            new_tms_line_sol = self.order_line.filtered(
                lambda L: L.product_id.tms_tracking == "line" and not L.tms_order_id
            )

            new_tms_orders |= self._tms_generate_line_tms_orders(new_tms_line_sol)

            return new_tms_orders

    def _tms_generation(self):
        """
        Create TMS Orders based on the products' configuration.
        :rtype: list(TMS Orders)
        :return: list of newly created TMS Orders
        """
        created_tms_orders = self.env["tms.order"]

        for sale in self:
            if not sale.tms_order_ids:
                new_tms_orders = self._tms_generate()

                if len(new_tms_orders) > 0:
                    created_tms_orders |= new_tms_orders
                    # If FSM Orders were created, post a message to the Sale Order
                    sale._post_tms_message(new_tms_orders)

        for tms_order in created_tms_orders:
            tms_order._onchange_scheduled_date_end()

        return created_tms_orders

    def _post_tms_message(self, tms_orders):
        """
        Post messages to the Sale Order and the newly created TMS Orders
        """
        self.ensure_one()
        msg_tms_links = ""
        for tms_order in tms_orders:
            tms_order.message_post_with_view(
                "mail.message_origin_link",
                values={"self": tms_order, "origin": self},
                subtype_id=self.env.ref("mail.mt_note").id,
                author_id=self.env.user.partner_id.id,
            )
            msg_tms_links += (
                " <a href=# data-oe-model=tms.order data-oe-id={}>{}</a>,".format(
                    tms_order.id, tms_order.name
                )
            )
        so_msg_body = _("TMS Order(s) Created: %s", msg_tms_links)
        self.message_post(body=so_msg_body[:-1])

    def _action_confirm(self):
        """On SO confirmation, some lines generate TMS orders."""
        result = super()._action_confirm()
        if any(
            sol.product_id.tms_tracking != "no"
            for sol in self.order_line.filtered(
                lambda x: x.display_type not in ("line_section", "line_note")
            )
        ):
            self._tms_generation()
        return result

    def action_view_tms_order(self):
        tms_orders = self.mapped("tms_order_ids")
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "tms.action_tms_dash_order"
        )
        if len(tms_orders) > 1:
            action["domain"] = [("id", "in", tms_orders.ids)]
        elif len(tms_orders) == 1:
            action["views"] = [(self.env.ref("tms.tms_order_view_form").id, "form")]
            action["res_id"] = tms_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action
