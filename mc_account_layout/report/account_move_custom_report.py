# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.tools import float_round


def get_hs_code_values(invoices):
    """
    Prepare values for the hs code table in Qweb reports.
    """
    sum_hs_code_details = {}
    hs_code_details = {}
    for invoice in invoices:
        hs_code_detail = {}
        for line in invoice.invoice_line_ids:
            hs_code = line.product_id.hs_code if line.product_id else False
            if hs_code:
                if hs_code not in hs_code_detail:
                    hs_code_detail[hs_code] = {'weight': float_round(line.quantity * line.product_id.weight, precision_rounding=0.01),
                                               'qty': line.quantity,
                                               'subtotal': line.price_subtotal, }
                else:
                    hs_code_detail[hs_code]['weight'] += float_round(line.quantity * line.product_id.weight, precision_rounding=0.01)
                    hs_code_detail[hs_code]['qty'] += line.quantity
                    hs_code_detail[hs_code]['subtotal'] += line.price_subtotal
        sum_weight = sum([hs_code_detail[hs_code]['weight'] for hs_code in hs_code_detail])
        sum_qty = sum([hs_code_detail[hs_code]['qty'] for hs_code in hs_code_detail])
        sum_subtotal = sum([hs_code_detail[hs_code]['subtotal'] for hs_code in hs_code_detail])
        sum_hs_code_details[invoice.id] = {'sum_weight': sum_weight, 'sum_qty': sum_qty, 'sum_subtotal': sum_subtotal, }
        hs_code_details[invoice.id] = hs_code_detail
    return sum_hs_code_details, hs_code_details


class InvoiceReport(models.Model):
    _name = 'report.account.report_invoice'

    def _get_report_values(self, docids, data=None):
        """
        Prepare values for the hs code table.
        """
        report = self.env['ir.actions.report']._get_report_from_name('account.report_invoice')
        invoices = self.env[report.model].browse(docids)
        sum_hs_code_details, hs_code_details = get_hs_code_values(invoices)
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': invoices,
            'data': data,
            'hs_code_details': hs_code_details,
            'sum_hs_code_details': sum_hs_code_details,
        }

class InvoiceReportWithPayments(models.Model):
    _name = 'report.account.report_invoice_with_payments'

    def _get_report_values(self, docids, data=None):
        """
        Prepare values for the hs code table.
        """
        report = self.env['ir.actions.report']._get_report_from_name('account.report_invoice_with_payments')
        invoices = self.env[report.model].browse(docids)
        sum_hs_code_details, hs_code_details = get_hs_code_values(invoices)
        return {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': invoices,
            'data': data,
            'hs_code_details': hs_code_details,
            'sum_hs_code_details': sum_hs_code_details,
        }
