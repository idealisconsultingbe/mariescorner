# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DescriptionLineValue(models.Model):
    _name = 'product.configurator.description.line.value'
    _description = 'Value of a Product Description Line'
    _order = 'id'

    type = fields.Selection([('attribute', 'Product Attribute'), ('text', 'Text')], string='Type', required=True)
    attribute_id = fields.Many2one('product.attribute', string='Product Attribute')
    description_line_id = fields.Many2one('product.configurator.description.line', string='Description Line', required=True, ondelete='cascade')
    text = fields.Char(string='Description', translate=True)

    @api.onchange('type')
    def _onchange_type(self):
        """ If type change, erase attribute and text """
        self.update({'attribute_id': False, 'text': ''})

    def name_get(self):
        """ Return text or attribute name according to type """
        result = []
        for record in self:
            if record.type == 'text':
                name = record.text
            else:
                if record.text:
                    name = "{} {}".format(record.text, record.attribute_id.name)
                else:
                    name = record.attribute_id.name
            result.append((record.id, '{}'.format(name)))
        return result
