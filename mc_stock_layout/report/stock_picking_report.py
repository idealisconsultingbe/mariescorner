# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools import html2plaintext


class PickingReport(models.AbstractModel):
    _name = 'report.mc_stock_layout.report_deliveryslip'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        show_delivery_comment = {doc.id: bool(html2plaintext(doc.sale_id.delivery_comment).strip()
                                              if doc.sale_id and doc.sale_id.delivery_comment else False) for doc in docs}
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'show_delivery_comment': show_delivery_comment,
        }

class PickingReport(models.AbstractModel):
    _name = 'report.mc_stock_layout.report_planned_deliveryslip'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        show_delivery_comment = {doc.id: bool(html2plaintext(doc.sale_id.delivery_comment).strip()
                                              if doc.sale_id and doc.sale_id.delivery_comment else False) for doc in docs}
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'show_delivery_comment': show_delivery_comment,
        }

class PickingReport(models.AbstractModel):
    _name = 'report.mc_stock_layout.report_fictitious_deliveryslip'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        show_delivery_comment = {doc.id: bool(html2plaintext(doc.sale_id.delivery_comment).strip()
                                              if doc.sale_id and doc.sale_id.delivery_comment else False) for doc in docs}
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'show_delivery_comment': show_delivery_comment,
        }
