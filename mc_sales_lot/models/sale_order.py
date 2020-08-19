# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """ Overridden Method
            Create Stock Production Sales Lot at order confirmation and update order lines accordingly.
            Sales Lots may be created automatically or manually according to configuration settings.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sales_lot.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        if production_lot_enabled:
            for order in self:
                for line in order.order_line.filtered(lambda l: l.has_tracking):
                    if not line.sales_lot_id:
                        name = self.env['ir.sequence'].next_by_code('stock.production.sales.lot') if automatic_lot_enabled else line.sales_lot_number
                        sales_lot_id = self.env['stock.production.sales.lot'].create({'name': name, 'product_id': line.product_id.id})
                        line.update({'sales_lot_id': sales_lot_id.id, 'sales_lot_number': name})
                    else:
                        line.update({'sales_lot_number': line.sales_lot_id.name})
        return super(SaleOrder, self)._action_confirm()
