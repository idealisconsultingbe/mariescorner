# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductAttributeCombination(models.Model):
    _name = 'product.attribute.combination'

    name = fields.Char(string="Name")
    attribute_ids = fields.Many2many('product.attribute', 'combination_attribute_rel', 'combination_id', 'attribute_id', string='Attributes', required=True)
    attribute_value_combination_ids = fields.One2many('product.attribute.combination.value', 'attribute_combination_id', string="Values combination")
    product_tmpl_ids = fields.Many2many('product.template', 'combination_product_rel', 'combination_id', 'product_id', string='Products', required=True)

    def set_product_attribute_exclusion(self):
        for pac in self:
            i = 0
            exclusions_values = {}
            for product_tmpl in pac.product_tmpl_ids:
                i += 1
                logging.info('%s product template attribute exclusion values configured' % (i))
                if i % 50 == 0:
                    configure_product_attribute_exclusion(exclusions_values)
                    exclusions_values = {}
            logging.info('%s product template attribute exclusion values configured' % (i))
            configure_product_attribute_exclusion(exclusions_values)

            session.env.cr.commit()
            session.close()
            logging.info('Done')
