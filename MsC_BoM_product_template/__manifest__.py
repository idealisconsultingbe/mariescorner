# -*- coding: utf-8 -*-
{
    'name': 'MsC BoM Product Template',
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Handling Product Templates in BoM',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mrp'],
    'data': [
        'views/mrp_bom_views.xml',
        'views/stock_move_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

