# Copyright 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TmsShipment(models.Model):

    _name = "tms.shipment"
    _description = "TMS Shipment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    active = fields.Boolean(default=True)

    name = fields.Char(
        required=True,
        copy=False,
        readonly=False,
        index="trigram",
        default=lambda self: _("New"),
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
        help="Company related to this shipment",
    )

    description = fields.Text()
    sequence = fields.Integer(default=10)

    route = fields.Boolean(string="Use predefined route")
    route_id = fields.Many2one("tms.route", string="Route")

    origin_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
        string="Origin Location",
    )
    destination_id = fields.Many2one(
        "res.partner",
        domain="[('tms_type', '=', 'location')]",
        context={"default_tms_type": "location"},
        string="Destination Location",
    )

    origin_location_id = fields.Many2one(
        "res.partner", compute="_compute_locations", store=True, string="Origin"
    )
    destination_location_id = fields.Many2one(
        "res.partner", compute="_compute_locations", store=True, string="Destination"
    )

    @api.depends("route", "route_id", "origin_id", "destination_id")
    def _compute_locations(self):
        for record in self:
            if record.route and record.route_id:
                record.origin_location_id = record.route_id.origin_location_id
                record.destination_location_id = record.route_id.destination_location_id
            else:
                record.origin_location_id = record.origin_id
                record.destination_location_id = record.destination_id

    driver_id = fields.Many2one(
        "res.partner",
        string="Driver",
        context={"default_tms_type": "driver"},
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    trailer_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        related="vehicle_id.tms_trailer_id",
        domain="[('vehicle_type', '=', 'trailer')]",
        string="Trailer",
        readonly=False,
        store=True,
    )
    team_id = fields.Many2one("tms.team", string="Team")
    crew_id = fields.Many2one("tms.crew", string="Crew")

    stage_id = fields.Many2one(
        "tms.stage",
        string="Stage",
        index=True,
        copy=False,
        domain="[('stage_type', '=', 'order')]",
        default=lambda self: self._default_stage_id(),
        group_expand="_read_group_stage_ids",
        ondelete="set null",
    )
    stage_name = fields.Char(related="stage_id.name")
    stage_decoration_color = fields.Selection(
        related="stage_id.stage_decoration_color", string="Stage Decoration Color"
    )
    custom_color = fields.Char(string="Custom Color", related="stage_id.custom_color")
    is_closed = fields.Boolean(
        "Is closed",
        related="stage_id.is_closed",
    )

    scheduled_date_start = fields.Datetime(
        string="Scheduled Start", default=datetime.now()
    )
    scheduled_duration = fields.Float(
        help="Scheduled duration of the work in" " hours",
    )
    scheduled_date_end = fields.Datetime(string="Scheduled End")

    start_trip = fields.Boolean(string="Trip Start", readonly=True)
    end_trip = fields.Boolean(string="Trip Finish", readonly=True)
    date_start = fields.Datetime(string="Actual Start")
    date_end = fields.Datetime(string="Actual End")
    duration = fields.Float(string="Actual Duration")

    diff_duration = fields.Float(
        readonly=True, string="Scheduled Duration - Actual Duration"
    )

    time_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Working Time')]",
        default=lambda self: self._default_time_uom_id(),
    )

    order_ids = fields.One2many("tms.order", "shipment_id", string="TMS Orders")

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company.currency_id,
    )

    tms_sorted_order_ids = fields.One2many(
        "tms.order",
        compute="_compute_sorted_order_lines",
        compute_sudo=True,
        string="TMS Orders Sorted",
    )

    @api.depends("order_ids", "order_ids.shipment_sequence")
    def _compute_sorted_order_lines(self):
        for order in self:
            order.tms_sorted_order_ids = order.order_ids.sorted(
                key=lambda line: line.shipment_sequence
            )

    driver_signature = fields.Binary(
        string="Driver Acceptance",
    )

    priority = fields.Selection(
        [("0", "Normal"), ("1", "Low"), ("2", "High"), ("3", "Very High")],
        string="Priority",
        help="Gives the sequence order when displaying a list of TMS shipments.",
    )

    color = fields.Integer("Color Index", default=0)

    tag_ids = fields.Many2many(
        "tms.tag",
        "tms_shipment_tag_rel",
        "tms_shipment_id",
        "tag_id",
        string="Tags",
        help="Classify and analyze your shipments",
    )

    kanban_state = fields.Selection(
        [("normal", "In Progress"), ("done", "Ready"), ("blocked", "Blocked")],
        string="Kanban State",
        copy=False,
        default="normal",
        required=True,
    )

    kanban_state_label = fields.Char(
        compute="_compute_kanban_state_label",
        string="Kanban State Label",
        tracking=True,
    )
    legend_blocked = fields.Char(
        related="stage_id.legend_blocked",
        string="Kanban Blocked Explanation",
        readonly=True,
        related_sudo=False,
    )
    legend_done = fields.Char(
        related="stage_id.legend_done",
        string="Kanban Valid Explanation",
        readonly=True,
        related_sudo=False,
    )
    legend_normal = fields.Char(
        related="stage_id.legend_normal",
        string="Kanban Ongoing Explanation",
        readonly=True,
        related_sudo=False,
    )

    total_amount = fields.Monetary(
        string="Total Amount", compute="_compute_total_amount", store=True
    )

    @api.depends("order_ids")
    def _compute_total_amount(self):
        for shipment in self:
            shipment.total_amount = shipment._get_total_amount()

    def _get_total_amount(self):
        self.ensure_one()
        total = 0.0
        # Logic to calculate total, to be extended by other modules
        return total

    @api.depends("stage_id", "kanban_state")
    def _compute_kanban_state_label(self):
        for record in self:
            if record.kanban_state == "normal":
                record.kanban_state_label = record.legend_normal
            elif record.kanban_state == "blocked":
                record.kanban_state_label = record.legend_blocked
            else:
                record.kanban_state_label = record.legend_done

    def _default_time_uom_id(self):
        # Fetch the value of default_time_uom from settings
        default_time_uom_id = (
            self.env["ir.config_parameter"].sudo().get_param("tms.default_time_uom")
        )

        # Return the actual record based on the ID retrieved from settings
        if default_time_uom_id:
            return self.env["uom.uom"].browse(int(default_time_uom_id))
        else:
            # If no default_time_uom is set, return None or a default value
            return self.env.ref("uom.product_uom_hour", raise_if_not_found=False)

    def _default_stage_id(self):
        stage = self.env["tms.stage"].search(
            [
                ("stage_type", "=", "order"),
            ],
            order="sequence asc",
            limit=1,
        )
        if stage:
            return stage
        raise ValidationError(_("You must create an TMS shipment stage first."))

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

    crew_active = fields.Boolean(compute="_compute_active_crew", store=True)

    # Constraints
    _sql_constraints = [
        ("name_uniq", "unique (name)", "Shipment name already exists!"),
        (
            "duration_ge_zero",
            "CHECK (scheduled_duration >= 0)",
            "Scheduled duration must be greater than or equal to zero!",
        ),
    ]

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env["tms.stage"].search([("stage_type", "=", "order")], order=order)

    def _stage_find(self, team_id=False, domain=None, order="sequence"):
        """Determine the stage of the current record with its teams, the given domain
        and the given team_id
        :param team_id
        :param domain : base search domain for stage
        :returns tms.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current records
        # team_ids = set()
        # if team_id:
        #     team_ids.add(team_id)
        # for record in self:
        #     if record.team_id:
        #         team_ids.add(record.team_id.id)
        # generate the domain

        search_domain = [("stage_type", "=", "order")]

        # if team_ids:
        #     search_domain += ['|', ('team_id', '=', False), ('team_id', 'in', list(team_ids))]
        # else:
        #     search_domain += [('team_id', '=', False)]

        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env["tms.stage"].search(search_domain, order=order, limit=1)

    @api.onchange("duration")
    def _onchange_duration(self):
        """Adjust date_end based on duration and date_start."""
        if self.date_start and self.date_end:
            self.date_end = self.date_start + timedelta(hours=self.duration)

    @api.onchange("date_end")
    def _onchange_date_end(self):
        """Adjust duration based on date_end and date_start, handle trip status.
        Handle scenarios where date_end is removed to correct an erroneous order."""
        if self.date_end and self.date_start:
            self._update_duration()
            if not self.end_trip:
                self.button_end_order()
        elif not self.date_end:
            # Case where date_end is being removed to correct an erroneous order
            self._handle_removed_end_date()
        if self.date_end and not self.date_start:
            self.date_start = self.date_end
            self.duration = 0

    @api.onchange("date_start")
    def _onchange_date_start(self):
        """Reset trip-related fields and handle date_end changes."""
        if not self.date_start:
            self._reset_trip_fields()
        else:
            self._onchange_date_end()
            if not self.date_end and not self.start_trip:
                self.button_start_order()

    def button_start_order(self):
        """Start a trip, set the date_start, and update driver stage."""
        if not self.date_start:
            self.date_start = fields.Datetime.now()
        self.start_trip = True
        # self._update_driver_stage(is_transit=True)
        self.stage_id = self._stage_find(domain=[("is_transit", "=", True)])

    def button_end_order(self):
        """End a trip, set the date_end, and calculate the duration and diff_duration."""
        self.date_end = fields.Datetime.now()
        self._update_duration()
        self.diff_duration = round(self.scheduled_duration - self.duration, 2)
        self.start_trip = False
        self.end_trip = True
        self.stage_id = self._stage_find(domain=[("is_closed", "=", True)])
        # self._update_driver_stage(is_transit=False)

    def button_refresh_duration(self):
        """Refresh the trip duration based on current date_end and date_start."""
        self.date_end = fields.Datetime.now()
        self._update_duration()

    def _update_duration(self):
        """Helper method to calculate and set the duration based on date_start and date_end."""
        self.duration = self._calculate_duration()

    def _calculate_duration(self):
        """Calculate the duration between date_start and date_end in hours."""
        if not self.date_start or not self.date_end:
            return 0
        duration = self.date_end - self.date_start
        return duration.total_seconds() / 3600

    def _reset_trip_fields(self):
        """Reset fields related to trip status."""
        self.start_trip = False
        self.end_trip = False
        self.date_end = False
        self.duration = 0
        self.diff_duration = 0
        # self._update_driver_stage()

    def _handle_removed_end_date(self):
        """Handle cases where date_end is removed to correct an erroneous order."""
        if self.date_start and not self.start_trip:
            self.end_trip = False
            self.button_start_order()
        else:
            self.end_trip = False
            # self._update_driver_stage()
        self.duration = 0
        self.diff_duration = 0

    # def _update_driver_stage(self, is_transit=None):
    #     """Update the driver's stage if necessary."""
    #     if self.driver_id:
    #         if (
    #             is_transit is None
    #             or self.driver_id.tms_stage_id.is_transit != is_transit
    #         ):
    #             self.driver_id._compute_tms_stage_id()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("tms.shipment")

        return super().create(vals_list)

    @api.onchange(
        "team_id",
        "driver_id",
        "crew_id",
        "vehicle_id",
        "route_id",
    )
    def _onchange_transport_data(self):
        for rec in self:
            for order in rec.order_ids:
                order.team_id = rec.team_id
                order.crew_id = rec.crew_id
                order.driver_id = rec.driver_id
                order.vehicle_id = rec.vehicle_id

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        for rec in self:
            for order in rec.order_ids:
                if order.stage_id.sequence <= rec.stage_id.sequence:
                    order.stage_id = rec.stage_id

    def update_tms_order_route(self):
        for order in self.order_ids:
            if self.route:
                if order.route:
                    order.route_id = self.route_id
                    order._onchange_route_id()
                    order._onchange_scheduled_duration()

    def update_tms_order_scheduled_date_start(self):
        for rec in self:
            for order in rec.order_ids:
                order.scheduled_date_start = rec.scheduled_date_start
                order._onchange_scheduled_date_start()
