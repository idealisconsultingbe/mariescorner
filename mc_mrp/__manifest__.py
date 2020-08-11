# -*- coding: utf-8 -*-
{
    'name': 'MsC BoM Product Template',
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Allow usage of product templates as BoM components.',
    'description': """
    In BoMs users can select product templates to fill components list.
    In the mto manufacturing process the right product product is automatically selected thanks to SO line attributes.
    """,
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['sale', 'mrp', 'purchase_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_template_attribute_value_views.xml',
        'views/mrp_bom_views.xml',
        'views/product_attribute_value_percentage_price_views.xml',
        'views/product_attribute_value_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

