# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tms Shipment",
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
        "wizards/tms_shipment_create.xml",
        "data/ir_sequence_data.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "security/tms_shipment.xml",
        "views/tms_order.xml",
        "views/tms_shipment.xml",
        "views/tms_shipment_report.xml",
        "views/menu.xml",
    ],
    "demo": [
        # 'demo/tms_order.xml',
        # 'demo/tms_shipment.xml',
    ],
}
