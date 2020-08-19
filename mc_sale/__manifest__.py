# -*- coding: utf-8 -*-
{
    'name': 'MsC Sales',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Modifications to sales processes and products',
    'description': """
    """,
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['sale', 'sale_product_configurator', 'purchase', 'product'],
    'data': [
        'views/product_attribute_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/assets.xml',
        'wizard/sale_product_configurator_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

