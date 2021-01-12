# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Care Form',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Mc Care Warranty',
    'description': """
    This module add a portal web survey that allows a customer to register is sale order as Mc Care.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['account', 'mc_sale', 'mc_sales_lot'],
    'data': [
        # 'views/res_partner_views.xml',
        'views/product_attribute_views.xml',
        'views/stock_production_sales_lot_views.xml',
        'views/mrp_production_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

