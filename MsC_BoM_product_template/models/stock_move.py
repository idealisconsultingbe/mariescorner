# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    # should be stored to prevent unwanted related=True behavior
    product_tmpl_id = fields.Many2one('product.template', store=True)
    # add product template to domain to prevent user from choosing a product not bound to product template
    product_id = fields.Many2one('product.product', domain="[('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
