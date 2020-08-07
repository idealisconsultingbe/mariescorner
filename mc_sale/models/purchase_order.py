# -*- coding: utf-8 -*-

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Generate the Sales Order Line values from the PO line
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        if line.move_dest_ids and len(line.move_dest_ids.mapped('sales_lot_id')) == 1 \
                and all(move.sales_lot_id for move in line.move_dest_ids):
            res['sales_lot_id'] = line.move_dest_ids[0].sales_lot_id.id
        return res

