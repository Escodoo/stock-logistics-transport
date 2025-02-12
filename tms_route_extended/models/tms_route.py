# Copyright 2025 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsRoute(models.Model):

    _inherit = "tms.route"

    region_type = fields.Selection(
        [("hub", "Hub"), ("inland", "Inland"), ("region", "Region")],
        string="Region Type",
        required=True,
    )
    type = fields.Selection(
        [("a", "A"), ("b", "B")], string="Operation Type", required=True
    )
    restricted = fields.Boolean(string="Restricted")
    pickup = fields.Boolean(string="Pickup")
    delivery = fields.Boolean(string="Delivery")
    deadline1 = fields.Integer(string="Deadline 1")
    deadline2 = fields.Integer(string="Deadline 2")
    quantity = fields.Integer(string="Quantity")
    value_td = fields.Float(string="TD Value")
    value_su = fields.Float(string="SU Value")
    value_pickup = fields.Float(string="Pickup Value")
    square = fields.Char(string="Square")
