# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': "MsC MRP Layout",
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Modifications to Manufacturing Orders layout',
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mc_mrp'],
    'data': [
        'views/mrp_production_templates.xml',
        'report/mrp_production_templates.xml',
        'report/mrp_production_report_views.xml'
    ],
    'installable': True,
    'auto_install': False,
}
