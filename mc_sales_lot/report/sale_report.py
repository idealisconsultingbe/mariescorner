# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    sales_lot_id = fields.Many2one('stock.production.sales.lot', 'Manufacturing Number', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['sales_lot_id'] = ', l.sales_lot_id as sales_lot_id'
        groupby += ', l.sales_lot_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
