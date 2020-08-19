# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one('product.product', required=False)
    product_uom_id = fields.Many2one(
        'uom.uom', domain="[('category_id', 'in', [product_uom_category_id, product_tmpl_uom_category_id])]")
    product_tmpl_uom_category_id = fields.Many2one('uom.category', related='product_tmpl_id.uom_id.category_id', string='Product Tmpl UOM Categ')
    # should be stored to prevent unwanted related=True behavior
    product_tmpl_id = fields.Many2one('product.template', store=True)
    product_attribute_ids = fields.Many2many('product.attribute', 'bom_line_product_attribute_rel', 'line_id', 'attribute_id', string='Product Attributes')
    allowed_attribute_ids = fields.Many2many('product.attribute', 'allowed_product_attribute_bom_line_rel', 'line_id', 'attribute_id', string='Allowed Product Attributes', compute='_compute_allowed_attribute_ids', help='Used in UI')

    @api.depends('product_tmpl_id', 'bom_id.product_tmpl_id')
    def _compute_allowed_attribute_ids(self):
        """
            Compute allowed attributes.
            Those attributes should be present in BoM product template and be related to attributes of BoM line product template
        """
        for line in self:
            if line.product_tmpl_id:
                line_product_attributes = line.product_tmpl_id.attribute_line_ids.mapped('attribute_id')
                bom_product_attributes = line.bom_id.product_tmpl_id.attribute_line_ids.mapped('attribute_id').filtered(lambda a: (a.product_attribute_ids | a.product_attribute_id) & line_product_attributes)
                line.allowed_attribute_ids = [(6, 0, bom_product_attributes.ids)]
            else:
                line.allowed_attribute_ids = []

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        """ Clear product field when product_tmpl changes """
        if self.product_id and self.product_tmpl_id and (self.product_tmpl_id != self.product_id.product_tmpl_id):
            temp = self.product_tmpl_id
            self.product_id = False
            self.update({'product_tmpl_id': temp})
