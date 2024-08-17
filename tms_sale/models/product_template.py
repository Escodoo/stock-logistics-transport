# Copyright (C) 2019 Brian McMaster
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    tms_product = fields.Boolean(string="Is a TMS Product?")

    tms_tracking = fields.Selection(
        [
            ("no", "Don't create TMS order"),
            ("sale", "Create one TMS order per sale order"),
            ("line", "Create one TMS order per sale order line"),
        ],
        default="no",
        string="TMS Tracking",
        help="""Determines what happens upon sale order confirmation:
                - None: nothing additional, default behavior.
                - Per Sale Order: One TMS Order will be created for the sale.
                - Per Sale Order Line: One TMS Order for each sale order line
                will be created.""",
    )
