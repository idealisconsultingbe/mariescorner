# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


{
    'name': "MsC Stock Layout",
    'version': '13.0.0.1',
    'category': 'Operations/Purchase',
    'summary': 'Modifications to Stock Qweb layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['web', 'mc_sales_lot', 'mc_sales_representative'],
    'data': [
        'data/data_reports.xml',
        'data/mail_data.xml',
        'views/stock_picking_views.xml',
        'report/stock_picking_templates.xml',
        'report/stock_picking_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
