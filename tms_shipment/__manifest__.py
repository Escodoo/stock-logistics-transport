# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS - Shipment",
    "summary": """
        TMS Shipment""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "tms",
    ],
    "data": [
        # views
        "views/tms_order.xml",
        "views/tms_shipment.xml",
        # reports
        "views/tms_shipment_report.xml",
        "views/tms_shipment_detailed_report.xml",
        "views/tms_shipment_driver_acceptance_report.xml",
        # wizards
        "wizards/tms_shipment_create.xml",
        # menu
        "views/menu.xml",
        # data
        "data/ir_sequence_data.xml",
        # security
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
        # 'demo/tms_order.xml',
        # 'demo/tms_shipment.xml',
    ],
}
