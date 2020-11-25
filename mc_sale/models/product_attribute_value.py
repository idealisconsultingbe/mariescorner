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
    is_none_value = fields.Boolean(string='Is None Value', default=False, help='If a value with this flag is chosen onto a sale order, no component line will be created for this attribute.')
    is_to_be_defined_value = fields.Boolean(string='Is To Be Defined Value', default=False, help='If a value with this flag is chosen onto a sale order, the MO will be blocked.')

    def _compute_length_uom_name(self):
        """ retrieve uom name from product template """
        for value in self:
            value.length_uom_name = self.env['product.template'].get_length_uom_name()
