# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS Geoengine",
    "summary": """
        TMS Geoengine""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "base_geoengine",
        "tms",
    ],
    "data": [
        "security/res_groups.xml",
        "views/tms_order.xml",
    ],
    "demo": [],
}
