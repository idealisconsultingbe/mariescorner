# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import logging


class ProductAttributeCombination(models.Model):
    _name = 'product.attribute.combination'

    name = fields.Char(string="Name")
    attribute_ids = fields.Many2many('product.attribute', 'combination_attribute_rel', 'combination_id', 'attribute_id', string='Attributes', required=True)
    does_exclude_attribute_id = fields.Many2one('product.attribute', string="Does Exclude", domain="[('id', 'in', attribute_ids)]", required=True)
    attribute_value_combination_ids = fields.One2many('product.attribute.combination.value', 'attribute_combination_id', string="Values combination")
    product_tmpl_ids = fields.Many2many('product.template', 'combination_product_rel', 'combination_id', 'product_id', string='Products', required=True)

    def inverse_attribute_combinaison(self):
        self.ensure_one()
        attribute_combination_inverse = {}
        for avc in self.attribute_value_combination_ids:
            vc_does_exclude = avc.value_combination_ids.filtered(lambda vc: vc.attribute_id.id == self.does_exclude_attribute_id)
            vc_to_be_allowed = avc.value_combination_ids.filtered(lambda vc: vc.attribute_id.id != self.does_exclude_attribute_id)
            for attribute_value in vc_does_exclude.value_ids:
                if attribute_value in attribute_combination_inverse:
                    for vc in vc_to_be_allowed:
                        if vc.attribute_id in attribute_combination_inverse[attribute_value]: 
                            attribute_combination_inverse[attribute_value][vc.attribute_id] |= vc.values_ids
                        else:
                            attribute_combination_inverse[attribute_value][vc.attribute_id] = vc.values_ids
                else:
                    attribute_combination_inverse[attribute_value] = {vc.attribute_id: vc.values_ids for vc in vc_to_be_allowed}
        return attribute_combination_inverse

    @api.model
    def get_unallowed_ptav(self, attribute_combination_inverse, does_exclude_ptav, product_tmpl):
        unallowed_ptav = self.env['product.template.attribute.value']
        for attribute, allowed_values in attribute_combination_inverse[does_exclude_ptav]:
            product_attribute_line = self.env['product.template.attribute.line'].search([('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', attribute.id)])
            unallowed_ptav |= self.env['product.template.attribute.value'].search(
                [('product_attribute_value_id', 'not in', allowed_values.ids),
                 ('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', attribute.id),
                 ('product_attribute_value_id', 'in', product_attribute_line.value_ids.ids)])
        return unallowed_ptav

    @api.model
    def configure_product_attribute_exclusion(self, exclusions_values):
        k = 0
        logging.info('Start configuring attributes combinaison.')
        for exclusion_id in exclusions_values:
            exclusion = self.env['product.template.attribute.exclusion'].browse(exclusion_id)
            exclusion.write({'value_ids': [(6, 0, exclusions_values[exclusion_id])]})
            k += 1
            if k % 100 == 0:
                logging.info('%s/%s product templates attribute exculsion configured' % (k, len(exclusions_values)))
                self.env.cr.commit()
        self.env.cr.commit()
        logging.info('%s/%s product templates attribute exculsion configured' % (k, len(exclusions_values)))

    def set_product_attribute_exclusion(self):
        for pac in self:
            i = 0
            attribute_combination_inverse = pac.inverse_attribute_combinaison()
            exclusions_values = {}
            for product_tmpl in pac.product_tmpl_ids:
                for does_exclude_attribute_value in attribute_combination_inverse:
                    does_exclude_ptav = self.env['product.template.attribute.value'].search([('name', '=', does_exclude_attribute_value), ('product_tmpl_id', '=', product_tmpl.id), ('attribute_id', '=', pac.does_exclude_attribute_id)])
                    unallowed_ptav = pac.get_unallowed_ptav(attribute_combination_inverse, does_exclude_ptav, product_tmpl)
                    if unallowed_ptav:
                        exclusion = does_exclude_ptav.exclude_for.filtered(
                            lambda ex: ex.product_tmpl_id.id == product_tmpl.id)
                        if not exclusion:
                            exclusion = self.env['product.template.attribute.exclusion'].create(
                                {'product_template_attribute_value_id': does_exclude_ptav.id,
                                 'product_tmpl_id': product_tmpl.id})
                        missing_values = unallowed_ptav - exclusion.value_ids
                        if missing_values:
                            if exclusions_values.get(exclusion.id, False):
                                exclusions_values[exclusion.id].extend(unallowed_ptav.ids)
                            else:
                                exclusions_values[exclusion.id] = unallowed_ptav.ids
                i += 1
                logging.info('%s product template attribute exclusion values configured' % (i))
                if i % 50 == 0:
                    pac.configure_product_attribute_exclusion(exclusions_values)
                    exclusions_values = {}
            logging.info('%s product template attribute exclusion values configured' % (i))
            pac.configure_product_attribute_exclusion(exclusions_values)
