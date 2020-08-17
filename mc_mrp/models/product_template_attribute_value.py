# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    price_extra = fields.Float(compute='_compute_price_extra', readonly=False, store=True)
    manual_price_extra = fields.Boolean(string='Manual Price', help='Used to prevent automatic computation of extra price', default=False)

    @api.depends(
        'product_tmpl_id.linear_length',
        'product_attribute_value_id.unit_price',
        'product_attribute_value_id.percentage_price_ids',
        'attribute_id.has_linear_price',
        'manual_price_extra')
    def _compute_price_extra(self):
        """ compute price only in particular cases :
        - if product attribute value has a 'percentage price' matching product category and price is not set on 'manual'
        - if product attribute has 'linear price' flag and price is not set on 'manual'
        """
        for value in self:
            if value.product_attribute_value_id.percentage_price_ids and not value.manual_price_extra:
                percentage_price = value._get_percentage_price(value.product_attribute_value_id.percentage_price_ids)
                if percentage_price:
                    value.price_extra = round(value.product_tmpl_id.list_price / 100) * percentage_price.percentage_price or 0.0
            elif value.attribute_id.has_linear_price and not value.manual_price_extra:
                value.price_extra = value.product_tmpl_id.linear_length * value.product_attribute_value_id.unit_price or 0.0
            else:
                value.price_extra = value.price_extra

    def _get_percentage_price(self, percentage_prices):
        for percentage_price in percentage_prices:
            if percentage_price.product_category_id == self.product_tmpl_id.categ_id and percentage_price.percentage_price:
                return percentage_price
