# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    tms_need_pickup_order = fields.Boolean("Need Pickup Order", default=False)

    tms_pickup_route_flag = fields.Boolean(string="Use predefined pickup route")
    tms_pickup_route_id = fields.Many2one("tms.route", string="Pickup Route")

    tms_pickup_origin_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
        string="Pickup Origin Location",
    )

    tms_pickup_destination_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
        string="Pickup Destination Location",
    )

    tms_pickup_scheduled_date_start = fields.Datetime(
        string="Pickup Scheduled Start", default=datetime.now()
    )
    tms_pickup_scheduled_date_end = fields.Datetime(string="Pickup Scheduled End")
    tms_pickup_scheduled_duration = fields.Float(string="Pickup Scheduled Duration")

    @api.onchange("tms_pickup_route_flag")
    def _onchange_tms_pickup_route_flag(self):
        if self.tms_pickup_route_flag:
            self.tms_pickup_origin_id = None
            self.tms_pickup_destination_id = None
        else:
            self.tms_pickup_route_id = None

    @api.onchange("tms_pickup_route_id")
    def _onchange_tms_pickup_route_id(self):
        if self.tms_pickup_route_flag:
            if self.tms_pickup_route_id.estimated_time_uom.name == "Days":
                self.tms_pickup_scheduled_duration = (
                    self.tms_pickup_route_id.estimated_time * 24
                )
            else:
                self.tms_pickup_scheduled_duration = (
                    self.tms_pickup_route_id.estimated_time
                )
        else:
            self.tms_pickup_scheduled_duration = 0.0

    @api.onchange("tms_pickup_scheduled_duration")
    def _onchange_tms_pickup_scheduled_duration(self):
        if self.tms_pickup_scheduled_date_start and self.tms_pickup_scheduled_duration:
            self.tms_pickup_scheduled_date_end = (
                self.tms_pickup_scheduled_date_start
                + timedelta(hours=self.tms_pickup_scheduled_duration)
            )

    @api.onchange("tms_pickup_scheduled_date_end")
    def _onchange_tms_pickup_scheduled_date_end(self):
        if self.tms_pickup_scheduled_date_end and self.tms_pickup_scheduled_date_start:
            difference = (
                self.tms_pickup_scheduled_date_end
                - self.tms_pickup_scheduled_date_start
            )
            self.tms_pickup_scheduled_duration = difference.total_seconds() / 3600

    @api.onchange("tms_pickup_scheduled_date_start")
    def _onchange_tms_pickup_scheduled_date_start(self):
        if self.tms_pickup_scheduled_date_start:
            # Se a data de fim estiver vazia e houver duração, calcula a data de fim
            if (
                self.tms_pickup_scheduled_duration
                and not self.tms_pickup_scheduled_date_end
            ):
                self.tms_pickup_scheduled_date_end = (
                    self.tms_pickup_scheduled_date_start
                    + timedelta(hours=self.tms_pickup_scheduled_duration)
                )
            # Se a data de fim estiver preenchida, ajusta conforme a duração
            elif self.tms_pickup_scheduled_date_end:
                self.tms_pickup_scheduled_date_end = (
                    self.tms_pickup_scheduled_date_start
                    + timedelta(hours=self.tms_pickup_scheduled_duration)
                )

    def _tms_generation(self):
        result = super()._tms_generation()
        if result:
            for sale in self.filtered(lambda x: x.tms_need_pickup_order):
                vals = sale._prepare_tms_pickup_order(so_id=sale.id)
                pickup_order = self.env["tms.order"].sudo().create(vals)
                pickup_order._onchange_scheduled_date_end()
                result |= pickup_order

        return result

    def _prepare_tms_pickup_order(self, **kwargs):
        """
        Prepare the values to create a new TMS Pickup Order from a sale order.
        """
        self.ensure_one()
        return {
            "sale_id": kwargs.get("so_id", False),
            "sale_line_id": kwargs.get("sol_id", False),
            "company_id": self.company_id.id,
            "route": self.tms_pickup_route_flag,
            "route_id": self.tms_pickup_route_id.id or None,
            "origin_id": self.tms_pickup_origin_id.id or None,
            "destination_id": self.tms_pickup_destination_id.id or None,
            "scheduled_date_start": self.tms_pickup_scheduled_date_start or None,
            "scheduled_date_end": self.tms_pickup_scheduled_date_end or None,
            "is_pickup_order": True,
        }
