# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    tms_shipment_id = fields.Many2one("tms.shipment", string="TMS Shipment")
