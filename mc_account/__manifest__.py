# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': "MsC Account",
    'version': '13.0.0.1',
    'category': 'Accounting/Accounting',
    'summary': 'Accounting Needs of MsC',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_sales_lot', 'mc_batch_picking', 'mc_sale'],
    'data': [
        'security/inter_company_groups.xml',
        'views/res_config_settings_views.xml',
        'views/purchase_order_views.xml',
        'wizard/create_vendor_bill_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
