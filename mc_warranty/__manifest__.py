# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Warranty',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'MsC Care Warranty Web Form',
    'description': """
    This module allows final customer to register their product if they have suscribed to a MsC Care warranty.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_sales_lot', 'website_form'],
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/stock_production_sales_lot_views.xml',
        'data/website_data.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

