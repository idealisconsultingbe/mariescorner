# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import api, models
from odoo.tools import float_round


class PartnerCustomReport(models.AbstractModel):
    _name = 'report.mc_sales_representative.sales_commissions_report'
    _description = 'Partner Custom Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """ Generate report values instead of complicated manipulation of records in Qweb """
        # retrieve representatives
        if not data:
            data = dict()
        if not docids:
            docids = data.get('representative_ids', self.sudo().env['res.partner'].search([('is_sales_representative', '=', True)]).ids)
        docs = self.sudo().env['res.partner'].browse(docids)

        # retrieve dates from parameters or use last month if dates are missing
        start_date = data.get('start_date', date.today().replace(day=1) + relativedelta(months=-1))
        end_date = data.get('end_date', date.today().replace(day=1) + relativedelta(days=-1))
        # since report_action() method convert dates to strings, we should convert them in order to compare dates
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%d/%m/%y').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%d/%m/%y').date()

        invoices_values = dict()
        for representative in docs:
            # retrieve customer invoices to which current representative is linked
            commissionned_invoices = self.env['account.move'].search([('type', 'in', ['out_invoice', 'out_refund']),
                                                                      ('sales_representative_id', '=', representative.id),
                                                                      ('state', 'not in', ['draft', 'cancel']),
                                                                      ('invoice_payment_state', '=', 'paid')])

            # create a dictionary with untaxed amount without shipping costs and last payment date for each invoice
            delivery_products = self.env['delivery.carrier'].search([]).mapped('product_id')
            delivery_accounts = self.env['account.account'].search([('is_transport', '=', True)])
            invoices_data = dict()
            for invoice in commissionned_invoices:
                payment_info = invoice._get_reconciled_info_JSON_values()
                if payment_info:
                    payment_date = [payment['date'] for payment in payment_info]
                    payment_date.append(invoice.invoice_date)
                else:
                    payment_date = [invoice.invoice_date]
                if invoice.is_outbound():
                    sign = -1
                else:
                    sign = 1
                last_payment_date = max(payment_date) if payment_date else False
                invoice_lines = invoice.mapped('invoice_line_ids').filtered(lambda line: line.product_id not in delivery_products and not line.account_id in delivery_accounts)
                untaxed_total_signed = sign * sum(invoice_lines.mapped('price_subtotal'))
                invoices_data[invoice.id] = {'last_payment': last_payment_date, 'amount_untaxed_signed': untaxed_total_signed}

            commercial_partners = commissionned_invoices.mapped('partner_id.commercial_partner_id')
            invoices = commissionned_invoices.filtered(lambda inv:
                                                       inv.amount_residual == 0.0 and invoices_data[inv.id].get('last_payment')
                                                       and start_date <= invoices_data[inv.id]['last_payment'] <= end_date)
            percentage = representative.commission_percentage
            invoices_values[representative.id] = {
                'total_commissions': 0.0,
                'total_invoiced': sum([invoices_data[inv.id].get('amount_untaxed_signed', 0.0) for inv in invoices]),
                'commission_percentage': percentage,
                'invoices': []
            }
            for partner in commercial_partners.sorted(key=lambda p: p.name):
                partner_invoices = invoices.filtered(lambda inv: inv.partner_id.commercial_partner_id == partner)
                lines = [{
                    'order_no': ', '.join([order.name for order in inv.invoice_line_ids.mapped('sale_line_ids.order_id')]),
                    'invoice_no': inv.name,
                    'invoice_date': inv.invoice_date,
                    'payment_date': invoices_data[inv.id].get('last_payment', ''),
                    'invoice_total': invoices_data[inv.id].get('amount_untaxed_signed', 0.0),
                    'commission_amount': float_round(invoices_data[inv.id].get('amount_untaxed_signed', 0.0) * percentage, precision_rounding=0.01, rounding_method='HALF-UP'),
                    'due_date': inv.invoice_date_due
                } for inv in partner_invoices]
                if lines:
                    invoices_values[representative.id]['invoices'].append({
                        'name': partner.name,
                        'ref': partner.ref,
                        'total': sum([invoices_data[inv.id].get('amount_untaxed_signed', 0.0) for inv in partner_invoices]),
                        'lines': lines,
                        'commissions': sum([line['commission_amount'] for line in lines])
                    })
            invoices_values[representative.id]['total_commissions'] = sum([invoice['commissions'] for invoice in invoices_values[representative.id]['invoices']])

        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'start_date': start_date,
            'end_date': end_date,
            'report_data': invoices_values
        }
