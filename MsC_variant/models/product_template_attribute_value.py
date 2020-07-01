# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    price_extra = fields.Float(compute='_compute_price_extra', store=True)

    @api.depends('product_tmpl_id.linear_length', 'product_attribute_value_id.unit_price', 'product_attribute_value_id.is_tlc')
    def _compute_price_extra(self):
        for value in self:
            if value.product_attribute_value_id.is_tlc:
                value.price_extra = round(value.product_tmpl_id.list_price / 100) * 10
            else:
                value.price_extra = value.product_tmpl_id.linear_length * value.product_attribute_value_id.unit_price
