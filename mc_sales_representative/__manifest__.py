# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Sales Representative',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Sales Representative PDF Report',
    'description': """
    This module allows creation of a report for sales representatives in order to track their commission.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['account', 'sale'],
    'data': [
        'views/account_account_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'report/res_partner_report.xml',
        'report/res_partner_report_templates.xml',
        'report/account_invoice_report_view.xml',
        'report/sale_report_views.xml',
        'wizard/print_sales_commissions_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

