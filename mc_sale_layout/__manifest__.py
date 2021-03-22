# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': "MsC Sale Layout",
    'version': '13.0.0.1',
    'category': 'Sales/Sales',
    'summary': 'Modifications to Sales Orders layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_sale', 'mc_sales_lot', 'mc_sales_representative'],
    'data': [
        'report/sale_order_templates.xml',
        'report/sale_report.xml',
        'views/sale_order_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
