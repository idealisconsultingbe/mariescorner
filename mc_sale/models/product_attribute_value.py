# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    def _default_length_uom(self):
        return self.env['product.template'].get_length_uom_name()

    unit_price = fields.Float('Unit Price', digits='Product Price', help='Price per length unit')
    length_uom_name = fields.Char(string='Length UoM Name', compute='_compute_length_uom_name', default=_default_length_uom, store=True)
    percentage_price_ids = fields.One2many('product.attribute.value.percentage.price', 'product_attribute_value_id', string='Percentage Price')
    has_linear_price = fields.Boolean(string='Linear Price', related='attribute_id.has_linear_price')

    def _compute_length_uom_name(self):
        """ retrieve uom name from product template """
        for value in self:
            value.length_uom_name = self.env['product.template'].get_length_uom_name()
