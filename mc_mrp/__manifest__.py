# -*- coding: utf-8 -*-
{
    'name': 'MsC BoM Product Template',
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Allow usage of product templates as BoM components.',
    'description': """
    In BoMs a components line can be related to a product template instead of a product product.
    If a MO is created manually components line will have to be completed -> the user will have to select the right product product.
    In the mto manufacturing process the right product product is automatically selected thanks to attributes selected through the product configurator.
    
    In order to be able to do this automatic selection of product product we had to linked product attributes between one another.
    """,
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['mrp', 'purchase_stock', 'mc_sale', 'mc_sales_lot'],
    'data': [
        'views/product_attribute_views.xml',
        'views/mrp_bom_views.xml',
        'views/product_attribute_value_views.xml',
        'views/mrp_production_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

