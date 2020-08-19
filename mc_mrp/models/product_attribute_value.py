# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

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

    @api.constrains('product_attribute_value_id', 'product_attribute_value_ids')
    def _check_product_attributes(self):
        """ Prevent user to use both product attribute value relationships """
        for value in self:
            if value.product_attribute_value_id and value.product_attribute_value_ids:
                raise UserError(_('There is already a relationship set on this attribute value ({}).').format(value.display_name))
