# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Manufacturing Number',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Allow to use Manufacturing Number.',
    'description': """
    This module adds manufacturing number logic.
    SO lines will ask for a manufacturing number if tracking is enabled on products and manufacturing numbers.
    Manufacturing numbers are created on SOs and are propagated in an UP BOTTOM way.
    It allows user to easily see which transfer is related to which so line.
    In case of a mto flow, manufacturing numbers will force a nomenclature for standard LOT / SN.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['purchase', 'mrp', 'inter_company_rules', 'sale_stock', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_production_sales_lot_groups.xml',
        'data/ir_sequence_data.xml',
        'data/report_paperformat_data.xml',
        'report/mrp_production_report_templates.xml',
        'report/mrp_production_report_views.xml',
        'report/sales_lot_report_templates.xml',
        'report/sales_lot_report_views.xml',
        'views/product_category_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/res_config_settings_views.xml',
        'views/stock_picking_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_move_views.xml',
        'views/stock_production_sales_lot_views.xml',
        'views/stock_production_sales_lot_templates.xml',
        'views/log_sales_lot_status_views.xml',
        'views/account_move_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

