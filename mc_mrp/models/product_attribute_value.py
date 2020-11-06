# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Related Value', domain="[('attribute_id', '=', related_product_attribute_id)]")
    product_attribute_value_ids = fields.One2many('product.attribute.value', 'product_attribute_value_id', string='Related Values', domain="[('attribute_id', 'in', related_product_attribute_ids)]")
    related_product_attribute_id = fields.Many2one('product.attribute', string='Related Attribute', related='attribute_id.product_attribute_id')
    related_product_attribute_ids = fields.One2many('product.attribute', 'product_attribute_id', string='Related Attributes', related='attribute_id.product_attribute_ids')
    relationship_type = fields.Selection([('o2m', 'One to Many'), ('m2o', 'Many to One'), ('none', 'None')], string='Relationship Type', compute='_compute_relationship_type', help='Utility field used in UI.')
    is_none_value = fields.Boolean(string='Is None Value', default=False, help='If a value with this flag is chosen onto a sale order, no component line will be created for this attribute.')
    is_to_be_defined_value = fields.Boolean(string='Is To Be Defined Value', default=False, help='If a value with this flag is chosen onto a sale order, the MO will be blocked.')

    def _compute_relationship_type(self):
        """ Compute relationship type in order to hide unwanted fields
            - if relationship_type = o2m, then m2o field should be hidden
            - if relationship_type = m2o, then o2m field should be hidden
            - else both fields should be visible
        """
        for value in self:
            if value.related_product_attribute_id:
                value.relationship_type = 'm2o'
            elif value.related_product_attribute_ids:
                value.relationship_type = 'o2m'
            else:
                value.relationship_type = 'none'

    @api.constrains('product_attribute_value_id', 'product_attribute_value_ids')
    def _check_product_attributes(self):
        """ Prevent user to use both product attribute value relationships """
        for value in self:
            if value.product_attribute_value_id and value.product_attribute_value_ids:
                raise UserError(_('There is already a relationship set on this attribute value ({}).').format(value.display_name))
