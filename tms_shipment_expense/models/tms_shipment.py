# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TmsShipment(models.Model):

    _inherit = "tms.shipment"

    expense_ids = fields.One2many("hr.expense", "tms_shipment_id")

    expense_total_amount = fields.Monetary(
        string="Total Expense Amount",
        compute="_compute_expense_total_amount",
        store=True,
        compute_sudo=True,
    )

    @api.depends("expense_ids", "expense_ids.total_amount")
    def _compute_expense_total_amount(self):
        for record in self:
            total_amount = sum(x.total_amount for x in record.expense_ids)
            record.expense_total_amount = total_amount

    employee_id = fields.Many2one(
        "hr.employee", string="Driver", compute="_compute_employee_id", store=True
    )

    @api.depends("driver_id")
    def _compute_employee_id(self):
        for record in self:
            record.employee_id = self.env["hr.employee"].search(
                [("user_partner_id", "=", record.driver_id.id)], limit=1
            )
            if not record.employee_id:
                record.employee_id = self.env["hr.employee"].search(
                    [("address_home_id", "=", record.driver_id.id)], limit=1
                )

    @api.depends("order_ids", "expense_ids")
    def _compute_total_amount(self):
        super()._compute_total_amount()

    def _get_total_amount(self):
        self.ensure_one()
        total = super()._get_total_amount()
        total += self.expense_total_amount
        return total
