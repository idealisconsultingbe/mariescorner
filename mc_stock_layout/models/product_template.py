# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_cms_uom_name(self):
        uom = self.env.ref('uom.product_uom_cm', raise_if_not_found=False)
        if not uom:
            categ = self.env.ref('uom.uom_categ_length')
            uom = self.env['uom.uom'].search([('category_id', '=', categ.id), ('uom_type', '=', 'smaller')], limit=1)
        return uom.name

    # weight uom name already exist on product.template model
    weight_net = fields.Float(string='Weight (net)', default=0.0, digits='Product Unit of Measure', help='Net weight net in kilograms')

    # use cms instead of meters as uom name
    cms_uom_name = fields.Char(string='Centimeters UoM Label', readonly=True, default=_default_cms_uom_name)
    height = fields.Float(string='Height', digits='Product Unit of Measure', default=0.0)
    width = fields.Float(string='Width', digits='Product Unit of Measure', default=0.0)
    depth = fields.Float(string='Depth', digits='Product Unit of Measure', default=0.0)

