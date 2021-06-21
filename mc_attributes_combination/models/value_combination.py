# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ValueCombinatioin(models.Model):
    _name = 'value.combination'

    combination_id = fields.Many2one('product.attribute.combination.value', string="Combination", required=True, ondelete='cascade')
    attribute_id = fields.Many2one('product.attribute', string='Attribute', required=True)
    value_ids = fields.Many2many('product.attribute.value', 'combination_value_value_rel', 'combination_value_id', 'value_id', string='Values', domain="[('attribute_id', '=', attribute_id)]")
