# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsOrder(models.Model):

    _inherit = "tms.order"

    shipment_id = fields.Many2one("tms.shipment", string="Shipment")

    shipment_sequence = fields.Integer(default=10)
