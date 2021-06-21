# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductAttributeCombination(models.Model):
    _name = 'product.attribute.combination'

    name = fields.Char(string="Name")
    attribute_ids = fields.Many2many('product.attribute', 'combination_attribute_rel', 'combination_id', 'attribute_id', string='Attributes', required=True)
    attribute_value_combination_ids = fields.One2many('product.attribute.combination.value', 'attribute_combination_id', string="Values combination")
    product_tmpl_ids = fields.Many2many('product.template', 'combination_product_rel', 'combination_id', 'product_id', string='Products', required=True)
