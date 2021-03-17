# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """
        Overriden standard method.
        Add sales_lot_id in order to populate it during mto process.
        """
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['sales_lot_id']
        return fields

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """
        Overriden standard method.
        Prevent procurement with different manufacturing numbers to be merged together!
        """
        if procurement.product_id.sales_lot_activated:
            key = procurement.product_id, procurement.product_uom, procurement.values.get('propagate_date'), procurement.values.get('propagate_date_minimum_delta'), procurement.values.get('propagate_cancel'), procurement.values.get('sales_lot_id')
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
            sales_lot = values.get('sales_lot_id', False)
            res['sales_lot_id'] = sales_lot if sales_lot else False
        return res