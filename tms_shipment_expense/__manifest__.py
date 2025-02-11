# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS - Shipment Expense",
    "summary": """
        TMS Shipment Expense""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "tms_shipment",
        "hr_expense",
    ],
    "data": [
        # views
        "views/tms_shipment.xml",
        "views/hr_expense.xml",
        # reports
        "views/tms_shipment_detailed_report.xml",
    ],
    "demo": [],
}
