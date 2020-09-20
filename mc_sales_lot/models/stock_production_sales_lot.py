# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ProductionSalesLot(models.Model):
    _name = 'stock.production.sales.lot'
    _description = 'Manufacturing Number'
    _order = 'name asc'
    _sql_constraints = [
        ('product_name_unique', 'UNIQUE(product_id, name)', _('You are about to use a lot number that already exists (product and manufacturing number combination must be unique).')),
    ]

    name = fields.Char(string='Manufacturing Number', required=True)
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

    def create_log(self, name, msg, user=None, model=None, record=None, datetime=None):
        """
        Create an entry log in order to track manufacturing number actions. In case of empty message,
        an error is thrown.
        :param name: name of the log
        :param msg: message recorded
        :param user: user who made the action
        :param model: ir.model where occurred the action
        :param record: the source record of the action
        :param datetime: the date and time when occurred the action
        :return: an entry log
        """
        self.ensure_one()
        if msg:
            vals = {
                'name': name,
                'description': msg,
                'sales_lot_id': self.id,
                'user_id': user.id or self.env.user.id,
                'model_id': model.id or False,
                'res_id': record or False,
                'date': datetime or fields.Datetime.now(),
            }
            return self.env['log.sales.lot.status'].create(vals)
        else:
            msg = _('You cannot create an empty log')
            if model and record:
                msg = '{} {}'.format(msg, _('(model={}, record={})').format(model.model, record))
            raise ValidationError(msg)

    def _get_sale_orders(self):
        """
        :return SO to which current manufacturing number is linked.
        """
        for sale_lot in self:
            sale_lot.sale_order_ids = sale_lot.sale_order_line_ids.mapped('order_id')

    def _get_lots(self):
        """
        :return S/N to which current manufacturing number is linked.
        """
        for sale_lot in self:
            sale_lot.lot_ids = sale_lot.stock_move_line_ids.mapped('lot_id')

    def _get_pickings(self):
        """
        :return transfers to which the manufacturing number is linked.
        """
        for sale_lot in self:
            sale_lot.picking_ids = sale_lot.stock_move_ids.mapped('picking_id')
