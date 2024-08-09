# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TmsShipment(models.Model):

    _inherit = "tms.shipment"

    purchase_ids = fields.One2many(
        "purchase.order",
        "tms_shipment_id",
        groups="purchase.group_purchase_user",
    )

    purchase_total_amount = fields.Monetary(
        string="Total Purchase Amount",
        compute="_compute_purchase_total_amount",
        store=True,
        compute_sudo=True,
    )

    @api.depends("purchase_ids", "purchase_ids.amount_total")
    def _compute_purchase_total_amount(self):
        for record in self:
            total_amount = sum(x.amount_total for x in record.purchase_ids)
            record.purchase_total_amount = total_amount

    @api.depends("order_ids", "purchase_ids")
    def _compute_total_amount(self):
        super()._compute_total_amount()

    def _get_total_amount(self):
        self.ensure_one()
        total = super()._get_total_amount()
        total += self.purchase_total_amount
        return total
