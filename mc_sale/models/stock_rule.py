# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        """ Overridden Method
            Add short description from sale order line to purchase order line
        """
        res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)
        sale_line = self.env['sale.order.line']
        if values.get('sale_line_id', False):
            sale_line = sale_line.browse(values.get('sale_line_id'))
        else:
            move_dest_ids = values.get('move_dest_ids', False)
            if move_dest_ids:
                sale_line = move_dest_ids[0]._get_sale_line()
        if sale_line:
            res['short_name'] = sale_line.short_name or ''
        return res
