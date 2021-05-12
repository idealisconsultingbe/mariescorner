# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


{
    'name': "MsC Stock Layout",
    'version': '13.0.0.1',
    'category': 'Operations/Purchase',
    'summary': 'Modifications to Stock Qweb layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_sale', 'mc_sales_lot', 'mc_sales_representative'],
    'data': [
        'data/data_reports.xml',
        'wizard/print_stock_report_views.xml',
        'views/stock_picking_views.xml',
        'report/sale_order_templates.xml',
        'report/sale_order_report.xml',
        'report/stock_picking_templates.xml',
        'report/stock_picking_report.xml',
        'views/product_template_views.xml',
        'data/mail_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
