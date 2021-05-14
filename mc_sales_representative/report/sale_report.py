# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    sales_representative_id = fields.Many2one('res.partner', 'Sales Representative', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['sales_representative_id'] = ', s.sales_representative_id as sales_representative_id'
        groupby += ', s.sales_representative_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
