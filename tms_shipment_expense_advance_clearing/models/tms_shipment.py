# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TmsShipment(models.Model):
    _inherit = "tms.shipment"

    expense_ids = fields.One2many(domain=[("advance", "=", False)])

    advance_ids = fields.One2many(
        "hr.expense.sheet",
        "tms_shipment_id",
        groups="hr_expense.group_hr_expense_team_approver",
        domain=[("advance", "=", True)],
    )

    advance_total_amount = fields.Monetary(
        string="Total Advance Amount",
        compute="_compute_advance_totals",
        store=True,
        compute_sudo=True,
    )
    clearing_total_amount = fields.Monetary(
        string="Total Clearing Amount",
        compute="_compute_advance_totals",
        store=True,
        compute_sudo=True,
    )
    advance_sheet_total_residual = fields.Monetary(
        string="Total Advance Sheet Residual",
        compute="_compute_advance_totals",
        store=True,
        compute_sudo=True,
    )
    amount_payable_total = fields.Monetary(
        string="Total Payable Amount",
        compute="_compute_advance_totals",
        store=True,
        compute_sudo=True,
    )

    @api.depends(
        "advance_ids.total_amount",
        "advance_ids.clearing_residual",
        "advance_ids.advance_sheet_residual",
        "advance_ids.amount_payable",
    )
    def _compute_advance_totals(self):
        for record in self:
            total_advance_amount = sum(
                advance.total_amount for advance in record.advance_ids
            )
            total_clearing_amount = sum(
                advance.clearing_residual for advance in record.advance_ids
            )
            total_advance_sheet_residual = sum(
                advance.advance_sheet_residual for advance in record.advance_ids
            )
            total_amount_payable = sum(
                advance.amount_payable for advance in record.advance_ids
            )

            record.advance_total_amount = total_advance_amount
            record.clearing_total_amount = total_clearing_amount
            record.advance_sheet_total_residual = total_advance_sheet_residual
            record.amount_payable_total = total_amount_payable

    @api.depends(
        "order_ids",
        "advance_ids",
        "advance_total_amount",
        "clearing_total_amount",
        "advance_sheet_total_residual",
        "amount_payable_total",
    )
    def _compute_total_amount(self):
        super()._compute_total_amount()

    def _get_total_amount(self):
        self.ensure_one()
        total = super()._get_total_amount()
        total += self.clearing_total_amount - self.amount_payable_total
        return total
