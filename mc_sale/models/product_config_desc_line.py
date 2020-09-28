# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class DescriptionLine(models.Model):
    _name = 'product.configurator.description.line'
    _description = 'Configuration of Product Description'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Sequence')
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    value_ids = fields.One2many('product.configurator.description.line.value', 'description_line_id', string='Values')
