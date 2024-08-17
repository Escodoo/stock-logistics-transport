# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Groups

    group_tms_team = fields.Boolean(
        string="TMS Manage Teams", implied_group="tms.group_tms_team"
    )
    group_tms_crew = fields.Boolean(
        string="TMS Manage Crews", implied_group="tms.group_tms_crew"
    )
    group_tms_driver_license = fields.Boolean(
        string="TMS Manage Driver License", implied_group="tms.group_tms_driver_license"
    )

    group_tms_vehicle_insurance = fields.Boolean(
        string="TMS Manage Vehicle Insurance",
        implied_group="tms.group_tms_vehicle_insurance",
    )

    group_tms_route = fields.Boolean(
        string="TMS Manage Routes", implied_group="tms.group_tms_route"
    )

    group_tms_route_stop = fields.Boolean(
        string="TMS Manage Route Stops", implied_group="tms.group_tms_route_stop"
    )

    group_tms_uom = fields.Boolean(
        string="TMS Units of Measure", implied_group="tms.group_tms_uom"
    )

    # Custom Fields

    tms_driver_license_security_days = fields.Integer(
        required=True,
        string="Driver license security days",
        config_parameter="tms.default_driver_license_security_days",
        default=30,
    )

    tms_vehicle_insurance_security_days = fields.Integer(
        required=True,
        string="Vehicle Insurance security days",
        config_parameter="tms.default_vehicle_insurance_security_days",
        default=30,
    )

    tms_length_uom = fields.Many2one(
        "uom.uom",
        default_model="res.config.settings",
        config_parameter="tms.default_length_uom",
        string="TMS Length Unit of Measure",
    )

    tms_distance_uom = fields.Many2one(
        "uom.uom",
        default_model="res.config.settings",
        config_parameter="tms.default_distance_uom",
        string="TMS Distance Unit of Measure",
    )

    tms_weight_uom = fields.Many2one(
        "uom.uom",
        default_model="res.config.settings",
        config_parameter="tms.default_weight_uom",
        string="TMS Weight Unit of Measure",
    )

    tms_speed_uom = fields.Many2one(
        "uom.uom",
        default_model="res.config.settings",
        config_parameter="tms.default_speed_uom",
        string="TMS Speed Unit of Measure",
    )

    tms_time_uom = fields.Many2one(
        "uom.uom",
        default_model="res.config.settings",
        config_parameter="tms.default_time_uom",
        string="TMS Time Unit of Measure",
    )
