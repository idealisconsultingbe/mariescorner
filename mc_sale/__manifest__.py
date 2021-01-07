# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Sales',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Modifications to sales processes and products',
    'description': """
    * Adapt the sale.product.configurator to the need of Maries Corner.
        - Add some fields in the product configurator.
        - Those fields could impact the price unit of the so line.
        - Limitations when the user change the product on an existing so line custom fields are not refresh and keeps the values of the previous product.
    * Add some fields to product.attributes, product.attribute.values and product.template.
        - The main purpose of those fields is to automatically calculate the extra price of the product attribute values
            1. depending on the product categories (thanks to a new model product.attribute.value.percentage.price).
            2. or on the linear length of tissue needed for the product.
    * If the confirmation of sale order creates a purchase order (for example in the MTO process) than we allow through a new  
      button to validate the PO from the SO.
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': ['sale_product_configurator', 'sale_management', 'purchase', 'product', 'website_sale_stock', 'inter_company_rules'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_attribute_value_percentage_price_views.xml',
        'views/product_attribute_views.xml',
        'views/product_attribute_value_views.xml',
        'views/product_template_attribute_value_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/assets.xml',
        'views/variant_templates.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/product_category_views.xml',
        'wizard/sale_product_configurator_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}

