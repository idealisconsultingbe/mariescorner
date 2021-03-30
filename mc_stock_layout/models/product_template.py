# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # uom names already exist on product.template model
    weight_net = fields.Float(string='Weight (net)', default=0.0, digits='Product Unit of Measure', help='Net weight net in kilograms')
    height = fields.Float(string='Height', digits='Product Unit of Measure', default=0.0)
    width = fields.Float(string='Width', digits='Product Unit of Measure', default=0.0)
    depth = fields.Float(string='Depth', digits='Product Unit of Measure', default=0.0)

