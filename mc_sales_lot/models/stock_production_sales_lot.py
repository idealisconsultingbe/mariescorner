# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProductionSalesLot(models.Model):
    _name = 'stock.production.sales.lot'
    _description = 'Production Sales Lot'
    _sql_constraints = [
        ('product_name_unique', 'UNIQUE(product_id, name)', _('You are about to use a lot number that already exists (product and sale lot number combination must be unique).')),
    ]

    name = fields.Text(string='Lot/Serial Number', required=True)
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('type', 'in', ['product', 'consu']), ('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True, ondelete='restrict', check_company=True)
