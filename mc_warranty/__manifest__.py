# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Warranty',
    'version': '13.0.0.2',
    'category': 'Sales',

    'summary': 'Mc Care Warranty',
    'description': """
    This module adds a web form that allows final customers to register their Mc Care warranty.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['account', 'mc_sale', 'mc_sales_lot', 'website_form'],
    'data': [
        'data/website_data.xml',
        'data/mail_data.xml',
        'report/mrp_production_templates.xml',
        'report/mrp_production_report_views.xml',
        'report/sales_lot_report_templates.xml',
        'views/res_partner_views.xml',
        'views/product_attribute_views.xml',
        'views/stock_production_sales_lot_views.xml',
        'views/mrp_production_views.xml',
        'views/sale_order_views.xml',
        'views/website_form_templates.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

