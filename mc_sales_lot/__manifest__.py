# -*- coding: utf-8 -*-

{
    'name': 'MsC Sales Lot',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Allow to use sales lot.',
    'description': """
    This module add the sale lots logic.
    SO line will ask for a sale lots if their product has a tracking enable.
    Sale lot are created on the SO and are propagated in a UP BOTTOM way.
    It allow the user to easily see which transfer is related to which so line.
    In the case of an mto flow sale lots will impose a nomenclature for standard LOT / SN.
    """,
    'author': 'dwa@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['purchase', 'mrp', 'inter_company_rules', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_production_sales_lot_groups.xml',
        'data/ir_sequence_data.xml',
        'views/sale_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_views.xml',
        'views/mrp_production_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

