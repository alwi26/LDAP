# -*- coding: utf-8 -*-
{
    "name": "Accounting Extension",
    "version": "18.0.0.0.0",
    "license": "OPL-1",
    "summary": "Accounting Extension",
    "category": "Accounting",
    "author": "Falinwa",
    "website": "https://www.falinwa.com",
    "support": "sales_indo@falinwa.com",
    "description": """
        Accounting Extension.
    """,
    "depends": ["accountant"],
    "data": [
        "security/ir.model.access.csv",
        "views/cds_pre_account_views.xml",
        "views/account_account_views.xml",
        "views/account_move_line_views.xml",
        "views/analytic_plan_mapping_views.xml",
        "views/spreadsheet_dashboard.xml",
        "wizards/recycle_journal.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
