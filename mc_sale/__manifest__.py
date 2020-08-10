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
    'depends': ['purchase', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_production_sales_lot_groups.xml',
        'data/ir_sequence_data.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_views.xml',
        'views/mrp_production_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

