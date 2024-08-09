# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "TMS - Shipment Expense Advance Clearing",
    "summary": """
        TMS Shipment Expense Advance Clearing""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-transport",
    "depends": [
        "tms_shipment_expense",
        "hr_expense_advance_clearing",
    ],
    "data": [
        # views
        "views/hr_expense.xml",
        "views/tms_shipment.xml",
        "views/hr_expense_sheet.xml",
        # reports
        "views/tms_shipment_detailed_report.xml",
        "views/tms_shipment_driver_acceptance_report.xml",
    ],
    "demo": [],
}
