# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TmsOrder(models.Model):

    _inherit = "tms.order"

    is_pickup_order = fields.Boolean("Is Pickup Order", default=False)
