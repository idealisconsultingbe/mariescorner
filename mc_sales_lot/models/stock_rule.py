# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """
        Overriden standard method.
        Prevent procurement with different manufacturing numbers to be merged together!
        """
        if procurement.product_id.sales_lot_activated:
            key = procurement.product_id, procurement.product_uom, procurement.values['propagate_date'], procurement.values['propagate_date_minimum_delta'], procurement.values['propagate_cancel'], procurement.values['sales_lot_id']
        else:
            key = super(StockRule, self)._get_procurements_to_merge_groupby(procurement)
        return key

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        """
        Overriden method
        Add sales lot from stock moves to values used for purchase order line creation
        """
        res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, values, po)
        move_dest_ids = values.get('move_dest_ids', False)
        if move_dest_ids:
            if move_dest_ids[0].sales_lot_id:
                res['sales_lot_id'] = move_dest_ids[0].sales_lot_id.id
        else:
            res['sales_lot_id'] = values.get('sales_lot_id', False)
        return res