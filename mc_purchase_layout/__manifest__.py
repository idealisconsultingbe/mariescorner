# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.


{
    'name': "MsC Purchase Layout",
    'version': '13.0.0.1',
    'category': 'Operations/Purchase',
    'summary': 'Modifications to Purchases Orders layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['purchase'],
    'data': [
        'report/purchase_quotation_templates.xml',
        'report/purchase_order_templates.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
