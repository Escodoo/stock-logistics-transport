# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Tms Shipment Order Pickup",
    "summary": """
        TMS Shipment Pickup""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "tms_shipment",
        "tms_order_pickup",
    ],
    "data": [
        "views/tms_shipment_report.xml",
        "views/tms_shipment.xml",
    ],
    "demo": [],
}
