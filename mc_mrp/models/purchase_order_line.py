# -*- coding: utf-8 -*-
from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Attribute Values', help='Product attribute values that do not create variants', ondelete='restrict')
    product_custom_attribute_value_ids = fields.Many2many('product.attribute.custom.value', string='Attribute Custom Values', help='Product attribute custom values that do not create variants', ondelete='restrict')
    comment = fields.Html(string="Comment")

