# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    manufacturing_state = fields.Selection([
        ('none', 'None'),
        ('to_produce', 'To Produce'),
        ('in_manufacturing', 'In Manufacturing'),
        ('validated', 'Validated'),
    ], string='Manufacturing Status', readonly=True, copy=False, index=True, tracking=True, store=True, compute='_compute_manufacturing_state')

    @api.depends('order_line.sales_lot_id', 'state')
    def _compute_manufacturing_state(self):
        for order in self:
            sales_lots = order.mapped('order_line.sales_lot_id')
            if not sales_lots or order.state == 'draft':
                order.manufacturing_state = 'none'
            elif order.state == 'sale':
                manuf_orders = sales_lots.mapped('production_ids')
                if not manuf_orders:
                    order.manufacturing_state = 'to_produce'
                elif all([mo.state in ['done', 'cancel'] for mo in manuf_orders]):
                    order.manufacturing_state = 'validated'
                else:
                    order.manufacturing_state = 'in_manufacturing'
            else:
                order.manufacturing_state = 'validated'

    def _action_confirm(self):
        """ Overridden Method
            Add context info to skip MO confirmation if this sale order creates a MO
        """
        self = self.with_context(skip_mo_confirmation=True)
        return super(SaleOrder, self)._action_confirm()
