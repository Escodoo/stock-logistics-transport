# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FleetVehicleModel(models.Model):

    _inherit = "fleet.vehicle.model"

    vehicle_type = fields.Selection(
        selection_add=[
            ("tractor", "Cargo Vehicle"),
            ("trailer", "Trailer"),
        ],
        ondelete={"tractor": "set default", "trailer": "set default"},
    )
