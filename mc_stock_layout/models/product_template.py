# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_net = fields.Float(string='Weight (net)', default=0.0, help="Weigt net in kilograms")
    height = fields.Float(string='Height (cm)', default=0.0)
    width = fields.Float(string='Width (cm)', default=0.0)
    depth = fields.Float(string='depth (cm)', default=0.0)
