# -*- coding: utf-8 -*-
{
    "name": "Analytic Distribution Control",
    "version": "18.0.0.0.0",
    "license": "OPL-1",
    "summary": "Analytic Distribution Control",
    "category": "Accounting",
    "author": "CLuedoo",
    "website": "https://www.cluedoo.com/shop/lic-clu-set-pnc-0022-analytic-distribution-control-6348",
    "support": "support@cluedoo.com",
    "description": "Module to control analytic distribution",
    "depends": [
        "analytic",
        "account",
    ],
    "data": [
        "views/groups.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fal_analytic_distribution_control/static/src/**",
        ],
        "web.qunit_suite_tests": [
            "fal_analytic_distribution_control/static/tests/*.js",
        ],
        'web.qunit_suite_tests': [
            'fal_analytic_distribution_control/static/tests/*.js',
        ],
    },
    "application": False,
    "images": ["static/description/fal_analytic_distribution_control.png"],
    "price": 150.0,
    "currency": "USD",
}
