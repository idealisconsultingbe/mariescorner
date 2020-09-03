# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class McSaleProductConfigurator(models.TransientModel):
    _inherit = 'sale.product.configurator'

    fabrics_meterage_needed = fields.Float(string="Meterage of fabrics")
    product_is_tailor_made = fields.Boolean(string='Is Tailor Made', related='product_template_id.tailor_made')
    standard_product_price = fields.Float(string="Standard Product Price", readonly=1)
    product_cost = fields.Float(string="Product Cost")
    comment = fields.Html(string="Comment")
