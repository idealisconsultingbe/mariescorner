# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductAttributeCombinationValue(models.Model):
    _name = 'product.attribute.combination.value'

    name = fields.Char(string="Name", compute='_get_name')
    sequence = fields.Integer("Sequence", default=10)
    attribute_combination_id = fields.Many2one('product.attribute.combination', string="Attribute combination", required=True, ondelete='cascade')
    attribute_ids = fields.Many2many('product.attribute', related="attribute_combination_id.attribute_ids", string='Attributes')
    value_combination_ids = fields.One2many('value.combination', 'combination_id', string='Values Combination')

    @api.depends('value_combination_ids.value_ids')
    def _get_name(self):
        for pacv in self:
            name = ''
            for v in pacv.value_combination_ids:
                if name:
                    name += ' : '
                name += ','.join(v.mapped('value_ids.name'))
            pacv.name = name

    def set_product_attribute_value_exclusion(self, product_tmpl, exclusions_values):
        self.ensure_one()
        secondary_value_combination = self.value_combination_ids.filtered(lambda v: v.set_exclusion)
        secondary_attribute_id = secondary_value_combination.attribute_id
        for secondary_attribute_value in secondary_value_combination.value_ids:
            product_template_secondary_attribute = self.env['product.template.attribute.value'].search(
                [('name', '=', secondary_attribute_value), ('product_tmpl_id', '=', product_tmpl.id),
                 ('attribute_id', '=', secondary_attribute_id)])
            allowed_product_template_main_attribute = self.env['product.template.attribute.value'].search(
                [('name', 'in', attribute_combinaison_inverse[secondary_attribute_value]),
                 ('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', main_attribute_id)])
            product_attribute_line = session.env['product.template.attribute.line'].search(
                [('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', main_attribute_id)])
            unallowed_ptav_main_attribute = session.env['product.template.attribute.value'].search(
                [('id', 'not in', allowed_product_template_main_attribute.ids),
                 ('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', main_attribute_id),
                 ('product_attribute_value_id', 'in', product_attribute_line.value_ids.ids)])
            if unallowed_ptav_main_attribute:
                exclusion = product_template_secondary_attribute.exclude_for.filtered(
                    lambda ex: ex.product_tmpl_id.id == product_tmpl.id)
                if not exclusion:
                    exclusion = session.env['product.template.attribute.exclusion'].create(
                        {'product_template_attribute_value_id': product_template_secondary_attribute.id,
                         'product_tmpl_id': product_tmpl.id})
                missing_values = unallowed_ptav_main_attribute - exclusion.value_ids
                if missing_values:
                    if exclusions_values.get(exclusion.id, False):
                        exclusions_values[exclusion.id].extend(unallowed_ptav_main_attribute.ids)
                    else:
                        exclusions_values[exclusion.id] = unallowed_ptav_main_attribute.ids
            return exclusions_values
