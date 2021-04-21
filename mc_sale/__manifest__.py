# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': 'MsC Sales',
    'version': '13.0.0.1',
    'category': 'Sales',
    'summary': 'Modifications to sales processes and products',
    'description': """
    *   Adapt the sale.product.configurator to the need of Maries Corner.
        - Add some fields in the product configurator.
        - Those fields could impact the price unit of the so line.
        - Limitations when the user change the product on an existing so line custom fields are not refresh and keeps the values of the previous product.
    *   Add some fields to product.attributes, product.attribute.values and product.template.
        - The main purpose of those fields is to automatically calculate the extra price of the product attribute values
            1. depending on the product categories (thanks to a new model product.attribute.value.percentage.price).
    *   Allow to define the render of the description of an so line thanks to a new model product.config.desc.line availbale on product.template.
        This rendered description is sent everywhere in Odoo -> so_line, po_line, invoice_line, mto process.
    *   Add eori fiels on the company.
    *   Allow to define a fabric product in the sales configuration.
    *   Automatically compute the carrier on sale.order depending on its delivery address.
    *   Filter fields delivery address and invoice address on sale.order depending on the selected partner. 
    """,
    'author': 'dwa@idealisconsulting, pfi@idealisconsulting - Idealis Consulting',
    'website': 'http://www.idealisconsulting.com',
    'depends': [
        'sale_product_configurator',
        'sale_management',
        'inter_company_rules',
        'purchase_stock',
        'delivery',
        'account'
    ],
    'data': [
        # data
        'data/mail_templates.xml',
        # security
        'security/ir.model.access.csv',
        'security/mc_sale_security_rule.xml',
        # views
        'views/ir_qweb_widget_templates.xml',
        'views/res_config_settings_views.xml',
        'views/product_attribute_value_percentage_price_views.xml',
        'views/product_attribute_views.xml',
        'views/product_attribute_value_views.xml',
        'views/product_template_attribute_value_views.xml',
        'views/product_template_views.xml',
        'views/product_product_views.xml',
        'views/sale_order_views.xml',
        'views/assets.xml',
        'views/variant_templates.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',
        'views/stock_picking_views.xml',
        'views/res_company_views.xml',
        'views/report_templates.xml',
        'views/delivery_view.xml',
        'views/product_views.xml',
        # wizard
        'wizard/sale_product_configurator_views.xml',
        # report
        'report/res_partner_templates.xml',
        'report/res_partner_report_views.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
