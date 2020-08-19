# -*- coding: utf-8 -*-
from odoo import fields, models, _


class PercentagePrice(models.Model):
    _name = 'product.attribute.value.percentage.price'
    _description = 'Extra Price of an Attribute Value Based on a Percentage of Product Price'
    _rec_name = 'product_category_id'
    _order = 'product_category_id'
    _sql_constraints = [
        ('product_attribute_category_unique', 'UNIQUE(product_attribute_value_id, product_category_id)', _('Product category and attribute value combination must be unique.')),
    ]

    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Product Attribute Value', required=True)
    percentage_price = fields.Float(string='Percentage Price')
    product_category_id = fields.Many2one('product.category', string='Product Category', required=True)
