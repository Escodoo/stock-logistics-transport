# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

TMS_DRIVER_LICENSE_TYPES = [
    ("A", "A - Motorcycles"),
    ("B", "B - Automobiles"),
    ("C", "C - Truck"),
    ("D", "D - Bus"),
]
TMS_LOCATION_TYPES = [("terrestrial", "Terrestrial")]


class ResPartner(models.Model):
    _inherit = "res.partner"
    # TMS Type
    tms_type = fields.Selection(
        string="Type",
        selection=[("driver", "Driver"), ("location", "Location")],
        default=lambda self: self.env.context.get("default_tms_type"),
    )

    # ------------------------------
    #            Driver
    # ------------------------------

    # Driver - Flags
    tms_is_external = fields.Boolean(string="External Driver")
    tms_is_training = fields.Boolean(string="In TMS Training")
    tms_is_active = fields.Boolean(string="Active on TMS", default=True)

    # Driver - Relations
    tms_vehicles_ids = fields.One2many("fleet.vehicle", "driver_id")
    tms_order_ids = fields.One2many("tms.order", "driver_id")

    # Driver - Type
    tms_driver_type = fields.Selection(
        string="Type", selection=[("terrestrial", "Terrestrial")]
    )

    # Driver - Relations
    tms_team_id = fields.Many2one("tms.team")
    tms_crew_ids = fields.Many2many(
        "tms.crew",
        "tms_crew_drivers_rel",
        string="Crews",
    )
    tms_stage_id = fields.Many2one(
        "tms.stage",
        string="Stage",
        index=True,
        copy=False,
        default=lambda self: self._default_tms_stage_id(),
        group_expand="_read_group_tms_stage_ids",
    )
    tms_stage = fields.Char(related="tms_stage_id.name")

    # ------------------------------
    #      Driver - Terrestrial
    # ------------------------------

    # Terrestrial - Licenses
    tms_driver_license_number = fields.Char()
    tms_driver_license_type = fields.Selection(
        string="License type", selection=TMS_DRIVER_LICENSE_TYPES
    )
    tms_driver_license_expiration_date = fields.Date()
    tms_driver_license_file = fields.Binary()

    # Terrestrial - Experience
    tms_distance_traveled = fields.Integer()
    tms_distance_traveled_uom = fields.Selection(selection=[("km", "km"), ("mi", "mi")])
    tms_driving_experience_years = fields.Integer()

    # ==========================================================================

    # Location - Types
    tms_location_type = fields.Selection(selection=TMS_LOCATION_TYPES)

    @api.model
    def _read_group_tms_stage_ids(self, stages, domain, order):
        return self.env["tms.stage"].search(
            [("stage_type", "=", "driver")], order=order
        )

    def _default_tms_stage_id(self):
        stage = self.env["tms.stage"].search(
            [("stage_type", "=", "driver")],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage.id
