# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_mc_care = fields.Boolean(string='MC Care', default=False, help='Must be set if this attribute allows to show whether a product is Mc Care.')
