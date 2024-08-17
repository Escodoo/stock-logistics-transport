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
    tms_vehicles_ids = fields.One2many(
        "fleet.vehicle", "driver_id", string="TMS Vehicles"
    )
    tms_order_ids = fields.One2many("tms.order", "driver_id", string="TMS Orders")

    # Driver - Type
    tms_driver_type = fields.Selection(
        string="TMS Driver Type", selection=[("terrestrial", "Terrestrial")]
    )

    # Driver - Relations
    tms_team_id = fields.Many2one("tms.team", string="TMS Team")
    tms_crew_ids = fields.Many2many(
        "tms.crew",
        "tms_crew_drivers_rel",
        string="TMS Crews",
    )
    tms_stage_id = fields.Many2one(
        "tms.stage",
        string="TMS Stage",
        index=True,
        copy=False,
        default=lambda self: self._default_tms_stage_id(),
        group_expand="_read_group_tms_stage_ids",
    )

    tms_stage = fields.Char(string="TMS Stage Name", related="tms_stage_id.name")
    tms_stage_decoration_color = fields.Selection(
        related="tms_stage_id.stage_decoration_color",
        string="TMS Stage Decoration Color",
    )

    # ------------------------------
    #      Driver - Terrestrial
    # ------------------------------

    # Terrestrial - Licenses
    tms_driver_license_number = fields.Char(string="Driver License Number")
    tms_driver_license_type = fields.Selection(
        string="Driver License type", selection=TMS_DRIVER_LICENSE_TYPES
    )
    tms_driver_license_expiration_date = fields.Date(
        string="Driver License Expiration Date"
    )
    tms_driver_license_file = fields.Binary(string="Driver License File")

    # Terrestrial - Experience
    tms_distance_traveled = fields.Integer(string="Distance Traveled")
    tms_distance_traveled_uom = fields.Selection(
        selection=[("km", "km"), ("mi", "mi")], string="Distance Traveled UOM"
    )
    tms_driving_experience_years = fields.Integer(string="Driving Experience Years")

    # ==========================================================================

    # Location - Types
    tms_location_type = fields.Selection(
        selection=TMS_LOCATION_TYPES, string="TMS Location Type"
    )

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

    @api.depends("tms_order_ids.start_trip", "tms_order_ids.end_trip")
    def _compute_tms_stage_id(self):
        transit_stage = self.env["tms.stage"].search(
            [("stage_type", "=", "driver"), ("is_transit", "=", True)],
            order="sequence asc",
            limit=1,
        )
        default_stage = self.env["tms.stage"].search(
            [("stage_type", "=", "driver"), ("is_default", "=", True)],
            order="sequence asc",
            limit=1,
        )
        for partner in self:
            orders_in_progress = self.env["tms.order"].search(
                [
                    ("driver_id", "=", partner.id),
                    ("stage_id.is_closed", "=", False),
                    ("start_trip", "=", True),
                ]
            )

            if orders_in_progress and transit_stage != partner.tms_stage_id:
                if transit_stage:
                    partner.tms_stage_id = transit_stage
                else:
                    partner.tms_stage_id = False
            else:
                partner.tms_stage_id = default_stage if default_stage else False

    @api.model
    def open_travel_orders(self):
        return {
            "name": "Travel Orders",
            "type": "ir.actions.act_window",
            "res_model": "tms.order",
            "view_mode": "tree,form",
            "domain": [
                ("driver_id", "=", self.id),
                ("company_id", "=", self.env.user.company_id.id),
            ],
            "context": {"default_driver_id": self.id},
        }
