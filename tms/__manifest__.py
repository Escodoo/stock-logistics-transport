# Copyright (C) 2018 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "TMS - Transportation Management System",
    "summary": "Manage Vehicles, Drivers, Routes and Trips",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "TMS",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "base",
        "uom",
        "fleet_vehicle_notebook",
        "base_geolocalize",
        "partner_contact_gender",
        "partner_contact_birthdate",
    ],
    "data": [
        "views/fleet_vehicle_model.xml",
        # Data
        "data/ir_sequence_data.xml",
        "data/module_category.xml",
        "data/tms_team.xml",
        "data/tms_stage.xml",
        "data/uom_category.xml",
        # Security
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        # Views
        "views/res_config_settings.xml",
        "views/res_partner.xml",
        "views/fleet_vehicle.xml",
        "views/tms_order.xml",
        "views/tms_stage.xml",
        "views/tms_tag.xml",
        "views/tms_team.xml",
        "views/tms_crew.xml",
        "views/tms_route.xml",
        "views/tms_order_report.xml",
        # Menus
        "views/menu.xml",
        "views/fleet_menu.xml",
    ],
    "demo": [
        "demo/fleet_vehicle_model.xml",
        "demo/fleet_vehicle.xml",
        "demo/res_partner.xml",
        "demo/tms_team.xml",
        "demo/tms_route.xml",
        "demo/tms_order.xml",
        "demo/tms_crew.xml",
        "demo/fleet_vehicle_model.xml",
    ],
    "application": True,
    "development_status": "Alpha",
    "maintainers": ["max3903", "santiagordz", "EdgarRetes"],
}
