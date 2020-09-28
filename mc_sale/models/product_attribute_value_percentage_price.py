# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,  _


class PercentagePrice(models.Model):
    _name = 'product.attribute.value.percentage.price'
    _description = 'Extra Price of an Attribute Value Based on a Percentage of Product Price'
    _rec_name = 'product_category_id'
    _order = 'product_category_id'
    _sql_constraints = [
        ('product_attribute_category_unique', 'UNIQUE(product_attribute_value_id, product_category_id)', _('Product category and attribute value combination must be unique.')),
    ]

    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Product Attribute Value', required=True)
    price_extra = fields.Float(string='Extra Price', default=0.0)
    type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Fix Amount')], sting='Type', default='percentage')
    percentage_price = fields.Float(string='Percentage Price', default=0.0, help='Value between 0 and 1 (e.g.: 0.5 = 50%).')
    product_category_id = fields.Many2one('product.category', string='Product Category', required=True)

    @api.onchange('type')
    def onchange_price(self):
        if self.type == 'percentage':
            self.price_extra = 0
        elif self.type == 'amount':
            self.percentage_price = 0
