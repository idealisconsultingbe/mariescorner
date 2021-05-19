# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models,  _
from odoo.exceptions import UserError


class PercentagePrice(models.Model):
    _name = 'product.attribute.value.percentage.price'
    _description = 'Extra Price of an Attribute Value Based on a Percentage of Product Price'
    _rec_name = 'product_category_id'
    _order = 'product_category_id'
    _sql_constraints = [
        ('product_attribute_category_unique', 'UNIQUE(product_attribute_value_id, product_category_id, company_id)', _('Product category and attribute value combination must be unique.')),
    ]

    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Product Attribute Value', required=True, ondelete='cascade')
    price_extra = fields.Float(string='Extra Price', default=0.0)
    type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Fix Amount')], sting='Type', default='percentage')
    percentage_price = fields.Float(string='Percentage Price', default=0.0, help='Value between 0 and 1 (e.g.: 0.5 = 50%).')
    product_category_id = fields.Many2one('product.category', string='Product Category', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    quantity_computation_type = fields.Selection([
        ('standard', 'Standard'),
        ('quantity', 'Fabric Quantity'),
        ('total_quantity', 'Total Fabric Quantity'),
    ], string='Quantity Computation Type', default='standard', required=True, help='How extra price is computed.\n'
             '  -Standard: do not use custom values.\n'
             '  -Quantity: use custom value set on current attribute value used on product (only available if attribute value is a fabric that uses custom values and has linear price).\n'
             '  -Total Quantity: use custom values set on all fabric attribute values used on product.')

    @api.onchange('type')
    def onchange_price(self):
        if self.type == 'percentage':
            self.price_extra = 0
        elif self.type == 'amount':
            self.percentage_price = 0

    @api.constrains('quantity_computation_type', 'product_attribute_value_id.is_custom', 'product_attribute_value_id.has_linear_price')
    def _check_quantity_computation_type(self):
        for percentage_price in self:
            if percentage_price.quantity_computation_type == 'quantity' and (not percentage_price.product_attribute_value_id.is_custom or not percentage_price.product_attribute_value_id.has_linear_price):
                raise UserError(_('Computation of extra prices cannot be quantity dependent if product attribute value is not custom '
                                  'or is not configurated with linear prices (see product attribute value {}).').format(percentage_price.product_attribute_value_id.display_name))


