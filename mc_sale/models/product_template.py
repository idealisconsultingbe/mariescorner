# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tailor_made = fields.Boolean(string='Is Tailor Made', default=False)
    has_attribute_tissue_1 = fields.Boolean(string='Has Attribute Tissue 1', compute='_get_attribute_tissue_category')
    has_attribute_tissue_2 = fields.Boolean(string='Has Attribute Tissue 2', compute='_get_attribute_tissue_category')

    @api.depends('attribute_line_ids.attribute_id.tissue_category')
    def _get_attribute_tissue_category(self):
        """
        Set the fields has_attribute_tissue_1 if the product has an attribute with a linear price and tissue category of type 1.
        Set the fields has_attribute_tissue_2 if the product has an attribute with a linear price and tissue category of type 2.
        """
        for product in self:
            attributes = product.mapped('attribute_line_ids.attribute_id').filtered(lambda att: att.has_linear_price)
            attribute_tissue_categories = set(attributes.mapped('tissue_category'))
            product.has_attribute_tissue_1 = True if 'tissue_1' in attribute_tissue_categories else False
            product.has_attribute_tissue_2 = True if 'tissue_2' in attribute_tissue_categories else False
