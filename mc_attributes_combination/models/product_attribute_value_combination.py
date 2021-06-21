# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductAttributeCombinationValue(models.Model):
    _name = 'product.attribute.combination.value'

    attribute_combination_id = fields.Many2one('product.attribute.combination', string="Attribute combination", required=True, ondelete='cascade')
    attribute_ids = fields.Many2many('product.attribute', related="attribute_combination_id.attribute_ids", string='Attributes')
    value_combination_ids = fields.One2many('value.combination', 'combination_id', string='Values Combination')

    @api.model
    def create(self, values):
        attribute_combination_value = super(ProductAttributeCombinationValue, self).create(values)
        val = {'value_combination_ids': [(0, 0, {'attribute_id': attribute.id, 'combination_id': attribute_combination_value.id}) for attribute in attribute_combination_value.attribute_ids]}
        attribute_combination_value.write(val)
        return attribute_combination_value
