# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """ Overridden Method
            Create Stock Production Sales Lot at order confirmation and update order lines accordingly.
            Sales Lots may be created automatically or manually according to configuration settings.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sales_lot.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        if production_lot_enabled and automatic_lot_enabled:
            for order in self:
                for line in order.order_line.filtered(lambda l: l.has_tracking and not l.sales_lot_id and l.product_id and l.product_id.sales_lot_activated):
                    name = self.env['ir.sequence'].next_by_code('stock.production.sales.lot')
                    sales_lot_id = self.env['stock.production.sales.lot'].create({'name': name, 'product_id': line.product_id.id})
                    line.update({'sales_lot_id': sales_lot_id.id})
        return super(SaleOrder, self)._action_confirm()
