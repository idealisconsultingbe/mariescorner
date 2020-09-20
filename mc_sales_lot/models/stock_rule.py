# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """
        Override standard method.
        Prevent procurement with different manufacturing number to be merged together!
        """
        if procurement.product_id.sales_lot_activated:
            key = procurement.product_id, procurement.product_uom, procurement.values['propagate_date'], procurement.values['propagate_date_minimum_delta'], procurement.values['propagate_cancel'], procurement.values['sales_lot_id']
        else :
            key = super(StockRule, self)._get_procurements_to_merge_groupby(procurement)
        return key
