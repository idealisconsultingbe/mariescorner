# -*- coding: utf-8 -*-

{
    'name': "MsC Sale Layout",
    'version': '13.0.0.1',
    'category': 'Sales/Sales',
    'summary': 'Modifications to Sales Orders layout',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['web', 'mc_sale', 'mc_sales_lot'],
    'data': [
        'report/sale_order_templates.xml',
        'report/sale_report.xml',
        'views/sale_order_templates.xml',
        'views/ir_qweb_widget_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
