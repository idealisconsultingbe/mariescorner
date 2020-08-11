# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    def _default_length_uom(self):
        return self.env['product.template'].get_length_uom_name()

    unit_price = fields.Float('Unit Price', digits='Product Price', help='Price per length unit')
    length_uom_name = fields.Char(string='Length UoM Name', compute='_compute_length_uom_name', default=_default_length_uom, store=True)
    percentage_price_ids = fields.One2many('product.attribute.value.percentage.price', 'product_attribute_value_id', string='Percentage Price')
    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Related Value')
    product_attribute_value_ids = fields.One2many('product.attribute.value', 'product_attribute_value_id', string='Related Values')
    relationship_type = fields.Selection([('o2m', 'One to Many'), ('m2o', 'Many to One'), ('none', 'None')], string='Relationship Type', compute='_compute_relationship_type', help='Utility field used in UI.')

    @api.depends('product_attribute_value_ids', 'product_attribute_value_id')
    def _compute_relationship_type(self):
        """ Compute relationship type in order to hide unwanted fields
            - if relationship_type = o2m, then m2o field should be hidden
            - if relationship_type = m2o, then o2m field should be hidden
            - else both fields should be visible
        """
        for value in self:
            if value.product_attribute_value_id:
                value.relationship_type = 'm2o'
            elif value.product_attribute_value_ids:
                value.relationship_type = 'o2m'
            else:
                value.relationship_type = 'none'

    def _compute_length_uom_name(self):
        """ retrieve uom name from product template """
        for value in self:
            value.length_uom_name = self.env['product.template'].get_length_uom_name()

    @api.constrains('product_attribute_value_id', 'product_attribute_value_ids')
    def _check_product_attributes(self):
        """ Prevent user to use both product attribute value relationships """
        for value in self:
            if value.product_attribute_value_id and value.product_attribute_value_ids:
                raise UserError(_('There is already a relationship set on this attribute value ({}).').format(value.display_name))

    # # one2one relationship
    # product_attribute_value_id = fields.Many2one('product.attribute.value', string='Related Value',
    #                                              compute='_compute_product_attribute_value_id', inverse='_inverse_product_attribute_value_id',
    #                                              store=True)
    # product_attribute_value_ids = fields.One2many('product.attribute.value', 'product_attribute_value_id', readonly=True, help='Utility field, not used in UI')
    #
    # def _compute_length_uom_name(self):
    #     """ retrieve uom name from product template """
    #     for value in self:
    #         value.length_uom_name = self.env['product.template'].get_length_uom_name()
    #
    # @api.depends('product_attribute_value_ids')
    # def _compute_product_attribute_value_id(self):
    #     """ one2one logic (see product_attribute.py)"""
    #     for value in self:
    #         if len(value.product_attribute_value_ids) > 0:
    #             value.product_attribute_value_id = value.product_attribute_value_ids[0]
    #         else:
    #             value.product_attribute_value_id = False
    #
    # def _inverse_product_attribute_value_id(self):
    #     """ one2one logic """
    #     for value in self:
    #         value.product_attribute_value_ids = [(6, 0, [value.product_attribute_value_id.id])]
