# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fabrics_meterage_needed = fields.Float(string="Meterage of fabrics", related="product_id.linear_length")
    product_sale_price = fields.Float(related="product_template_id.list_price", string="Standard Sale Price")
    comment = fields.Html(string="Comment")
