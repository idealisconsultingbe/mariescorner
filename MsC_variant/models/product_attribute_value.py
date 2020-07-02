# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    def _default_length_uom(self):
        return self.env['product.template'].get_length_uom_name()

    unit_price = fields.Float('Unit Price', digits='Product Price', help='Price per length unit')
    length_uom_name = fields.Char(string='Length UoM Name', compute='_compute_length_uom_name', default=_default_length_uom, store=True)
    is_tlc = fields.Boolean(string='Is TLC', help='Customer provides his own fabric. Price is 10% of product price rounded to the nearest ten.')
    # one2one relationship
    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Related Value',
                                                 compute='_compute_product_attribute_value_id', inverse='_inverse_product_attribute_value_id',
                                                 store=True)
    product_attribute_value_ids = fields.One2many('product.attribute.value', 'product_attribute_value_id', readonly=True, help='Utility field, not used in UI')

    def _compute_length_uom_name(self):
        """ retrieve uom name from product template """
        for value in self:
            value.length_uom_name = self.env['product.template'].get_length_uom_name()

    @api.depends('product_attribute_value_ids')
    def _compute_product_attribute_value_id(self):
        """ one2one logic (see product_attribute.py)"""
        for value in self:
            if len(value.product_attribute_value_ids) > 0:
                value.product_attribute_value_id = value.product_attribute_value_ids[0]
            else:
                value.product_attribute_value_id = False

    def _inverse_product_attribute_value_id(self):
        """ one2one logic """
        for value in self:
            value.product_attribute_value_ids = [(6, 0, [value.product_attribute_value_id.id])]
