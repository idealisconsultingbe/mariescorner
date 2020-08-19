# -*- coding: utf-8 -*-

from odoo import models, fields, api


class McSaleProductConfigurator(models.TransientModel):
    _inherit = 'sale.product.configurator'

    tissue_meterage_1 = fields.Float(string="Meterage of tissue 1")
    tissue_meterage_2 = fields.Float(string="Meterage of tissue 2")
    has_attribute_tissue_1 = fields.Boolean(string='Has Attribute Tissue 1', related='product_template_id.has_attribute_tissue_1', help='Technical field that tells whether we have to display the field tissue_meterage_1')
    has_attribute_tissue_2 = fields.Boolean(string='Has Attribute Tissue 2', related='product_template_id.has_attribute_tissue_2', help='Technical field that tells whether we have to display the field tissue_meterage_2')
    product_is_tailor_made = fields.Boolean(string='Is Tailor Made', related='product_template_id.tailor_made')
    standard_product_price = fields.Float(string="Standard Product Price", readonly=1)
    product_cost = fields.Float(string="Product Cost")
    comment = fields.Html(string="Comment")
