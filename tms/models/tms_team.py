# Copyright (C) 2024 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TMSTeam(models.Model):
    _name = "tms.team"
    _description = "Transport Management System Team"

    def _default_stages(self):
        return self.env["tms.stage"].search([("is_default", "=", True)])

    @api.depends("order_ids")
    def _compute_order_count(self):
        order_data = self.env["tms.order"].read_group(
            [("team_id", "in", self.ids), ("stage_id.is_closed", "=", False)],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_count = result.get(team.id, 0)

    def _compute_order_need_assign_count(self):
        order_data = self.env["tms.order"].read_group(
            [
                ("team_id", "in", self.ids),
                ("driver_id", "=", False),
                ("stage_id.is_closed", "=", False),
            ],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_assign_count = result.get(team.id, 0)

    def _compute_order_need_schedule_count(self):
        order_data = self.env["tms.order"].read_group(
            [
                ("team_id", "in", self.ids),
                ("scheduled_date_end", "=", False),
                ("stage_id.is_closed", "=", False),
            ],
            ["team_id"],
            ["team_id"],
        )
        result = {data["team_id"][0]: int(data["team_id_count"]) for data in order_data}
        for team in self:
            team.order_need_schedule_count = result.get(team.id, 0)

    @api.depends("driver_ids")
    def _compute_driver_count(self):
        order_data = self.env["res.partner"].read_group(
            [("tms_team_id", "in", self.ids)],
            ["tms_team_id"],
            ["tms_team_id"],
        )
        result = {
            data["tms_team_id"][0]: int(data["tms_team_id_count"])
            for data in order_data
        }
        for team in self:
            team.driver_count = result.get(team.id, 0)

    @api.depends("vehicle_ids")
    def _compute_vehicle_count(self):
        order_data = self.env["fleet.vehicle"].read_group(
            [("tms_team_id", "in", self.ids)],
            ["tms_team_id"],
            ["tms_team_id"],
        )
        result = {
            data["tms_team_id"][0]: int(data["tms_team_id_count"])
            for data in order_data
        }
        for team in self:
            team.vehicle_count = result.get(team.id, 0)

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    description = fields.Text()
    color = fields.Integer("Color Index")
    stage_ids = fields.Many2many(
        "tms.stage",
        "tms_order_team_stage_rel",
        "team_id",
        "stage_id",
        string="Stages",
        default=_default_stages,
    )
    order_ids = fields.One2many(
        "tms.order",
        "team_id",
        string="Orders",
        domain=[("stage_id.is_closed", "=", False)],
    )
    order_count = fields.Integer(
        string="Orders Count", compute="_compute_order_count", store=True
    )

    order_need_assign_count = fields.Integer(
        compute="_compute_order_need_assign_count", string="Orders to Assign"
    )
    order_need_schedule_count = fields.Integer(
        compute="_compute_order_need_schedule_count", string="Orders to Schedule"
    )

    sequence = fields.Integer(default=1, help="Used to sort teams. Lower is better.")

    vehicle_ids = fields.One2many(
        "fleet.vehicle", "tms_team_id", domain="[('vehicle_type', '!=', 'trailer')]"
    )
    vehicle_count = fields.Integer(
        compute="_compute_vehicle_count", string="Vehicles Count", store=True
    )

    driver_ids = fields.One2many(
        "res.partner",
        "tms_team_id",
        domain=[("tms_type", "=", "driver")],
        context={"default_tms_type": "driver"},
    )
    driver_count = fields.Integer(
        compute="_compute_driver_count", string="Drivers Count", store=True
    )

    crew_ids = fields.One2many("tms.crew", "team_id")

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this order",
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Team name already exists!")]
