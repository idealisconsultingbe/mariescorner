# -*- coding: utf-8 -*-

from odoo import models, fields, api


class McSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tissue_meterage_1 = fields.Float(string="Meterage of tissue 1", default=0.0)
    tissue_meterage_2 = fields.Float(string="Meterage of tissue 2", default=0.0)
    product_price = fields.Float(related="product_template_id.list_price", string="Product Price")
    product_cost = fields.Float(related="product_template_id.standard_price", string="Product Cost")
    comment = fields.Html(string="Comment")
