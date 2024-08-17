# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TmsShipmentCreate(models.TransientModel):
    _name = "tms.shipment.create"
    _description = "TMS Shipment Wizard Create"

    team_id = fields.Many2one("tms.team", string="Team")
    crew_id = fields.Many2one("tms.crew", string="Crew")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        related="vehicle_id.tms_trailer_id",
        domain="[('vehicle_type', '=', 'trailer')]",
        string="Trailer",
        readonly=False,
    )
    driver_id = fields.Many2one(
        "res.partner",
        string="Driver",
        context={"default_tms_type": "driver"},
    )
    route = fields.Boolean(string="Use predefined route")
    route_id = fields.Many2one("tms.route", string="Route")

    origin_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
    )
    destination_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
    )

    scheduled_date_start = fields.Datetime(
        string="Scheduled Start", default=datetime.now()
    )
    scheduled_duration = fields.Float(
        help="Scheduled duration of the work in" " hours",
    )
    scheduled_date_end = fields.Datetime(string="Scheduled End")

    @api.onchange("route")
    def _onchange_route(self):
        if self.route:
            self.origin_id = None
            self.destination_id = None
        else:
            self.route_id = None

    @api.onchange("route_id")
    def _onchange_route_id(self):
        if self.route:
            if self.route_id.estimated_time_uom.name == "Days":
                self.scheduled_duration = self.route_id.estimated_time * 24
            else:
                self.scheduled_duration = self.route_id.estimated_time
        else:
            self.scheduled_duration = 0.0

    @api.onchange("scheduled_duration")
    def _onchange_scheduled_duration(self):
        if self.scheduled_date_start and self.scheduled_duration:
            self.scheduled_date_end = self.scheduled_date_start + timedelta(
                hours=self.scheduled_duration
            )

    @api.onchange("scheduled_date_end")
    def _onchange_scheduled_date_end(self):
        if self.scheduled_date_end and self.scheduled_date_start:
            difference = self.scheduled_date_end - self.scheduled_date_start
            self.scheduled_duration = difference.total_seconds() / 3600

    @api.onchange("scheduled_date_start")
    def _onchange_scheduled_date_start(self):
        if self.scheduled_date_start:
            # Se a data de fim estiver vazia e houver duração, calcula a data de fim
            if self.scheduled_duration and not self.scheduled_date_end:
                self.scheduled_date_end = self.scheduled_date_start + timedelta(
                    hours=self.scheduled_duration
                )
            # Se a data de fim estiver preenchida, ajusta conforme a duração
            elif self.scheduled_date_end:
                self.scheduled_date_end = self.scheduled_date_start + timedelta(
                    hours=self.scheduled_duration
                )

    @api.depends("team_id.driver_ids", "crew_id.driver_ids")
    def _compute_driver_ids_domain(self):
        all_drivers = self.env["res.partner"].search([("tms_type", "=", "driver")])
        all_driver_ids = all_drivers.ids
        for order in self:
            order.driver_ids_domain = [(6, 0, all_driver_ids)]
            if order.team_id:
                order.driver_ids_domain = [(6, 0, order.team_id.driver_ids.ids)]
            if order.crew_id:
                order.driver_ids_domain = [(6, 0, order.crew_id.driver_ids.ids)]

    driver_ids_domain = fields.Many2many(
        "res.partner",
        "team_drivers_rel",
        compute="_compute_driver_ids_domain",
        default=lambda self: self.env["res.partner"]
        .search([("tms_type", "=", "driver")])
        .ids,
    )

    @api.depends("team_id")
    def _compute_vehicle_ids_domain(self):
        all_vehicles = self.env["fleet.vehicle"].search(
            [("vehicle_type", "!=", "trailer")]
        )
        all_vehicles_ids = all_vehicles.ids
        for order in self:
            order.vehicle_ids_domain = [(6, 0, all_vehicles_ids)]
            if order.team_id:
                order.vehicle_ids_domain = [(6, 0, order.team_id.vehicle_ids.ids)]

    vehicle_ids_domain = fields.Many2many(
        "fleet.vehicle",
        "team_vehicles_rel",
        compute="_compute_vehicle_ids_domain",
        default=lambda self: self.env["fleet.vehicle"].search([]).ids,
    )

    @api.depends("team_id")
    def _compute_crew_ids_domain(self):
        all_crews = self.env["tms.crew"].search([])
        all_crews_ids = all_crews.ids

        if self.team_id:
            self.crew_ids_domain = [(6, 0, self.team_id.crew_ids.ids)]
        else:
            self.crew_ids_domain = [(6, 0, all_crews_ids)]

    crew_ids_domain = fields.Many2many(
        "tms.crew",
        "team_crews_rel",
        compute="_compute_crew_ids_domain",
        default=lambda self: self.env["tms.crew"].search([]).ids,
    )

    @api.depends("crew_id")
    def _compute_active_crew(self):
        for order in self:
            order.crew_active = bool(order.crew_id)
            if order.crew_id:
                order.vehicle_id = order.crew_id.default_vehicle_id.id
            else:
                order.vehicle_id = order.vehicle_id

    crew_active = fields.Boolean(compute="_compute_active_crew")

    overwrite_route_data = fields.Boolean(string="Overwrite Order Route", default=False)
    overwrite_scheduled_date = fields.Boolean(
        string="Overwrite Order Scheduled Date", default=False
    )

    def create_shipment(self):
        active_ids = self.env.context.get("active_ids", [])
        if not active_ids:
            return

        orders = self.env["tms.order"].browse(active_ids)
        if any(order.shipment_id for order in orders):
            raise UserError(_("One or more orders already have a shipment"))

        if any(order.stage_id.is_closed for order in orders):
            raise UserError(_("One or more orders are in a closed stage"))

        shipment = self.env["tms.shipment"].create(
            {
                "name": self.env["ir.sequence"].next_by_code("tms.shipment") or "New",
                "team_id": self.team_id.id or None,
                "crew_id": self.crew_id.id or None,
                "vehicle_id": self.vehicle_id.id or None,
                "trailer_id": self.trailer_id.id or None,
                "driver_id": self.driver_id.id or None,
                "route": self.route,
                "route_id": self.route_id.id or None,
                "origin_id": self.origin_id.id or None,
                "destination_id": self.destination_id.id or None,
                "scheduled_date_start": self.scheduled_date_start or None,
                "scheduled_duration": self.scheduled_duration or None,
                "scheduled_date_end": self.scheduled_date_end or None,
                "order_ids": [(6, 0, active_ids)],
            }
        )

        shipment.order_ids.write(
            {
                "team_id": shipment.team_id.id or None,
                "crew_id": shipment.crew_id.id or None,
                "driver_id": shipment.driver_id.id or None,
                "vehicle_id": shipment.vehicle_id.id or None,
                "trailer_id": shipment.trailer_id.id or None,
            }
        )

        if self.overwrite_route_data:
            for order in shipment.order_ids:
                if self.route:
                    if order.route_id:
                        order.write(
                            {
                                "route_id": self.route_id.id,
                                "route": True,
                            }
                        )

        if shipment.route:
            shipment._onchange_route_id()
            shipment._onchange_scheduled_duration()

        if self.overwrite_scheduled_date:
            shipment.order_ids.write(
                {
                    "scheduled_date_start": shipment.scheduled_date_start,
                    "scheduled_duration": self.scheduled_duration,
                    "scheduled_date_end": shipment.scheduled_date_end,
                }
            )

        return {
            "type": "ir.actions.act_window",
            "name": "Shipment",
            "res_model": "tms.shipment",
            "res_id": shipment.id,
            "view_mode": "form",
            "target": "current",
        }
