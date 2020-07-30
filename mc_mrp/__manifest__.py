# -*- coding: utf-8 -*-
{
    'name': 'MsC BoM Product Template',
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Allow to create a BoM with only product template in its components.',
    'description': """
    In BoMs it is possible to select only product template in its components.
    In the mto manufacturing process the right product product is automatically selected depending on the attributes selected on the SO.
    """,
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['sale', 'mrp'],
    'data': [
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_template_attribute_value_views.xml',
        'views/mrp_bom_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

