# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': "MsC Account Layout",
    'version': '13.0.0.1',
    'category': 'Accounting/Accounting',
    'summary': 'Modifications to Invoice layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_sale', 'mc_sales_lot', 'l10n_be_intrastat'],
    'data': [
        'report/report_invoice_templates.xml',
        'data/mail_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
