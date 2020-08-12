# -*- coding: utf-8 -*-

from odoo import models, fields, api


class McSaleProductConfigurator(models.TransientModel):
    _inherit = 'sale.product.configurator'

    # hide_advanced_options = fields.Boolean(string="Hide Advance Option", default=True)
    tissue_meterage_1 = fields.Float(string="Meterage of tissue 1")
    tissue_meterage_2 = fields.Float(string="Meterage of tissue 2")
    product_price = fields.Float(string="Product Price", readonly=1)
    product_cost = fields.Float(string="Product Cost", readonly=1)
    comment = fields.Html(string="Comment")

    # @api.onchange('hide_advanced_options')
    # def show_hide_advanced_options(self):
    #     self.ensure_one()
