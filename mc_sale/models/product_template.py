# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_length_uom(self):
        return self.get_length_uom_name()

    tailor_made = fields.Boolean(string='Is Tailor Made', default=False)
    has_attribute_tissue_1 = fields.Boolean(string='Has Attribute Tissue 1', compute='_get_attribute_tissue_category')
    has_attribute_tissue_2 = fields.Boolean(string='Has Attribute Tissue 2', compute='_get_attribute_tissue_category')
    linear_length = fields.Float('Linear Length', digits='Product Unit of Measure', default=0.0, help='Quantity of fabric required to upholster furniture')
    length_uom_name = fields.Char(string='Length UoM Label', compute='_compute_length_uom_name', default=_default_length_uom, store=True)

    def _compute_length_uom_name(self):
        for template in self:
            template.length_uom_name = self.get_length_uom_name()

    @api.model
    def get_length_uom_name(self):
        """ Retrieve reference uom name for length measures.
        It is possible to change this easily to use uom from ir.config.parameter for example """
        uom = self.env.ref('uom.product_uom_meter', False) or self.env['uom.uom'].search(
            [('measure_type', '=', 'length'), ('uom_type', '=', 'reference')], limit=1)
        return uom.name

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
