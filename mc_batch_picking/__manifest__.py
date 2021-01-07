# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': 'MsC Batch Picking',
    'version': '13.0.0.1',
    'category': 'Operations/Inventory',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['stock_picking_batch', 'delivery', 'mc_sales_lot'],
    'data': [
        'views/stock_picking_batch_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

