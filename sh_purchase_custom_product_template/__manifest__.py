# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Purchase Order Template Product",
    "author": "Softhealer Technologies & IT4LIFE",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "14.0.1",
    "category": "Purchases",
    "summary": """po product template app, build products combo odoo, purchase order custom template, request for quotation product, make template of rfq module""",
    "description": """This module useful to define multipe products in one custom template and load all products on single click in purchase order.
    po product template app, build products combo odoo, purchase order custom template, request for quotation product, make template of rfq module
    """,
    "depends": [
        'purchase'
    ],
    "data": [
        'security/purchase_custom_product_template_security.xml',
        'security/ir.model.access.csv',
        'views/purchase_template_product.xml',
        'views/bom_custom.xml',
        'views/production_custom.xml',
        'wizard/custom_product_template_views.xml',
    ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/SBLgzWir9wE",
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "20",
    "currency": "EUR"
}
