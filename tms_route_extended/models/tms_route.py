# Copyright 2025 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsRoute(models.Model):
    _inherit = "tms.route"

    region_type = fields.Selection(
        [
            ("hub", "Hub"),
            ("inland", "Inland"),
            ("region", "Region"),
        ],
        string="Region Type",
        default="hub",
        required=True,
        help="Specifies the type of region for this route.",
    )
    freight_type = fields.Selection(
        [
            ("both", "Both"),
            ("cif", "CIF"),
            ("fob", "FOB"),
        ],
        string="Freight Type",
        default="both",
        required=True,
        help="Indicates the type of freight agreement for this route.",
    )
    has_delivery_restriction = fields.Boolean(
        string="Delivery Restriction",
        default=False,
        help="Indicates whether there are delivery restrictions on this route.",
    )
    restriction_note = fields.Text(
        string="Restriction Notes",
        help="Provides additional information about any delivery restrictions.",
    )
    enabled_pickup = fields.Boolean(
        string="Pickup Enabled",
        default=True,
        help="Indicates if pickup service is available for this route.",
    )
    delivery_deadline = fields.Integer(
        string="Delivery Deadline (days)",
        default=1,
        help="Number of days required to complete delivery on this route.",
    )
    toll_quantity = fields.Integer(
        string="Toll Count", help="Number of tolls on this route."
    )
    additional_cost = fields.Float(
        string="Additional Delivery Cost",
        help="Extra cost due to delivery difficulties, tolls, or services.",
    )
    delivery_value = fields.Float(
        string="Pickup/Delivery Fee",
        help="Fee charged for pickup or delivery services on this route.",
    )
    commercial_area = fields.Char(
        string="Sales Area", help="Identifies the commercial area served by this route."
    )
