# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
{
    'name': 'MsC BoM Product Template',
    'version': '13.0.0.1',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Allow usage of product templates as BoM components.',
    'description': """
    -   In BoMs a components line can be related to a product template instead of a product product.
        If a MO is created manually components line will have to be completed -> the user will have to select the right product product.
        In the mto manufacturing process the right product product is automatically selected thanks to attributes selected through the product configurator.
    -   In the mto manufacturing process block the automatic validation of the MO -> MO have to be validated manually
    -   Allow to link product.attribute between each other, this feature is used during the mto process in order to select the right product.product on bom.line.
        Idem with product.attribute.value
    -   Allow to specify that a category is a category of 'foots'.
    -   Add boolean fields on product.product in order to detect if they are 'foots' or 'fabrics'
    -   Determine the extra price of a product.attribute.template value combination from the price of its corresponding product.variant.
    -   When creating variant automatically fulfill their default_code.
    -   During inter company pruchase -> sale creation automatically trigger product_id_on_change on every line of the SO.
    -   Add manufacturing state on SO.
    -   Allow to validate mto PO from their corresponding SO.
    -    
    
    In order to be able to do this automatic selection of product product we had to linked product attributes between one another.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['purchase_stock', 'mc_warranty'],
    'data': [
        'report/mrp_production_templates.xml',
        'report/sales_lot_report_templates.xml',
        'views/product_attribute_views.xml',
        'views/mrp_bom_views.xml',
        'views/mrp_bom_line_views.xml',
        'views/product_attribute_value_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_production_sales_lot_views.xml',
        'views/product_category_views.xml',
        'views/sale_order_views.xml',
        'wizard/confirm_purchase_order_views.xml'
    ],
    'auto_install': False,
    'installable': True,
    'application': True,
}

