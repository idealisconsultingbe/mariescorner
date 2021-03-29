# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Attribute Values', help='Product attribute values that do not create variants', ondelete='set null')
    product_custom_attribute_value_ids = fields.Many2many('product.attribute.custom.value', string='Attribute Custom Values', help='Product attribute custom values that do not create variants', ondelete='set null')
    comment = fields.Html(string='Comment')
