# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ProductionSalesLot(models.Model):
    _name = 'stock.production.sales.lot'
    _description = 'Production Sales Lot'
    _order = 'name asc'
    _sql_constraints = [
        ('product_name_unique', 'UNIQUE(product_id, name)', _('You are about to use a lot number that already exists (product and sale lot number combination must be unique).')),
    ]

    name = fields.Char(string='Lot/Serial Number', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('type', 'in', ['product', 'consu']), ('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True, ondelete='restrict', check_company=True)
    production_ids = fields.One2many('mrp.production', 'sales_lot_id', string='Manufacturing Orders')
    stock_move_ids = fields.One2many('stock.move', 'sales_lot_id', string='Stock Move Lines')
    stock_move_line_ids = fields.One2many('stock.move.line', 'sales_lot_id', string='Stock Move Lines')
    sale_order_line_ids = fields.One2many('sale.order.line', 'sales_lot_id', string='Sale Order Lines')
    sale_order_ids = fields.Many2many('sale.order', stirng='Sale Orders', compute='_get_sale_orders')
    lot_ids = fields.Many2many('stock.production.lot', stirng='Lot/Serial', compute='_get_lots')
    picking_ids = fields.Many2many('stock.picking', stirng='Transfers', compute='_get_pickings')
    log_sales_lot_status_ids = fields.One2many('log.sales.lot.status', 'sales_lot_id', string='Status')

    def _get_sale_orders(self):
        """
        :return SO at which the sale lot is linked.
        """
        for sale_lot in self:
            sale_lot.sale_order_ids = sale_lot.sale_order_line_ids.mapped('order_id')

    def _get_lots(self):
        """
        :return serials at which the sale lot is linked.
        """
        for sale_lot in self:
            sale_lot.lot_ids = sale_lot.stock_move_line_ids.mapped('lot_id')

    def _get_pickings(self):
        """
        :return transfers at which the sale lot is linked.
        """
        for sale_lot in self:
            sale_lot.picking_ids = sale_lot.stock_move_ids.mapped('picking_id')
