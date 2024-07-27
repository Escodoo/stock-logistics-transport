# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # Groups

    group_tms_team = fields.Boolean(
        string="Manage Teams", implied_group="tms.group_tms_team"
    )
    group_tms_crew = fields.Boolean(
        string="Manage Crews", implied_group="tms.group_tms_crew"
    )
    group_tms_driver_license = fields.Boolean(
        string="Manage Driver License", implied_group="tms.group_tms_driver_license"
    )

    group_tms_vehicle_insurance = fields.Boolean(
        string="Manage Vehicle Insurance",
        implied_group="tms.group_tms_vehicle_insurance",
    )

    group_tms_route = fields.Boolean(
        string="Manage Routes", implied_group="tms.group_tms_route"
    )

    group_tms_route_stop = fields.Boolean(
        string="Manage Route Stops", implied_group="tms.group_tms_route_stop"
    )

    group_tms_uom = fields.Boolean(
        string="Units of Measure", implied_group="tms.group_tms_uom"
    )

    # Custom Fields

    driver_license_security_days = fields.Integer(
        required=True,
        string="Driver license security days",
        config_parameter="tms.default_driver_license_security_days",
    )

    vehicle_insurance_security_days = fields.Integer(
        required=True,
        string="Vehicle Insurance security days",
        config_parameter="tms.default_vehicle_insurance_security_days",
    )

    tms_length_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Length / Distance')]",
        default_model="res.config.settings",
        config_parameter="tms.default_length_uom",
    )

    tms_distance_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Length / Distance')]",
        default_model="res.config.settings",
        config_parameter="tms.default_distance_uom",
    )

    tms_weight_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Weight')]",
        default_model="res.config.settings",
        config_parameter="tms.default_weight_uom",
    )

    tms_speed_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Speed')]",
        default_model="res.config.settings",
        config_parameter="tms.default_speed_uom",
    )

    tms_time_uom = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', 'Working Time')]",
        default_model="res.config.settings",
        config_parameter="tms.default_time_uom",
    )
