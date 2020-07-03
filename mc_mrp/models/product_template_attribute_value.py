# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    price_extra = fields.Float(compute='_compute_price_extra', readonly=False, store=True)
    manual_price_extra = fields.Boolean(string='Manual Price', help='Used to prevent automatic computation of extra price')

    @api.depends(
        'product_tmpl_id.linear_length',
        'product_attribute_value_id.unit_price',
        'product_attribute_value_id.is_tlc',
        'attribute_id.has_linear_price',
        'manual_price_extra')
    def _compute_price_extra(self):
        """ compute price only in particular cases :
        - if product attribute value has 'TLC' flag and price is not set on 'manual'
        - if product attribute has 'fabric attribute' flag and price is not set on 'manual'
        """
        for value in self:
            if value.product_attribute_value_id.is_tlc and not value.manual_price_extra:
                value.price_extra = round(value.product_tmpl_id.list_price / 100) * 10
            elif value.attribute_id.has_linear_price and not value.manual_price_extra:
                value.price_extra = value.product_tmpl_id.linear_length * value.product_attribute_value_id.unit_price or 0.0
            else:
                value.price_extra = value.price_extra
