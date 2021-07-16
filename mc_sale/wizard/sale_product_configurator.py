# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class McSaleProductConfigurator(models.TransientModel):
    _inherit = 'sale.product.configurator'

    fabrics_meterage_needed = fields.Float(string="Meterage of fabrics")
    product_is_tailor_made = fields.Boolean(string='Is Tailor Made', related='product_template_id.tailor_made')
    standard_product_price = fields.Float(string="Standard Product Price", readonly=1)
    product_cost = fields.Float(string="Product Cost", readonly=1)
    comment = fields.Text(string="Comment")
    manual_description = fields.Text(string='Manual Description', help='Additional information added to short description in report')
