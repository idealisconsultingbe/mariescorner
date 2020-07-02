# -*- coding: utf-8 -*-
{
    'name': 'MsC Variant',
    'version': '13.0.0.1',
    'category': 'Sales/Sales',
    'summary': 'Compute Price of Product Variants According to Attributes and Link Attributes to Each Others',
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['product', 'sale'],
    'data': [
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_template_attribute_value_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

