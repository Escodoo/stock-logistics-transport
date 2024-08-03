# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS - Sale Order Pickup",
    "summary": """
        TMS Sale Pickup Order""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "tms_sale",
        "tms_order_pickup",
    ],
    "data": [
        "views/sale_order.xml",
    ],
    "demo": [],
}
