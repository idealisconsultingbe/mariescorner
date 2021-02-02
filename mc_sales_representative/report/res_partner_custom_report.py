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

        # generate a dictionary with all values required by report template
        # structure:
        # { representative_id: {
        #     'total_commissions': value,
        #     'total_invoiced': value,
        #     'commission_percentage': value,
        #     'all_invoices': [ {
        #             'customer_name': value,
        #             'customer_reference': value,
        #             'customer_invoices_total': value,
        #             'customer_commissions_total': value,
        #             'customer_invoices': [ {
        #                     'order_name': value,
        #                     'invoice_name': value,
        #                     'invoice_date': value,
        #                     'invoice_amount': value,
        #                     'commission_amount': value,
        #                     'invoice_due_date': value,
        #                     } ]
        #             } ]
        #     }
        # }
        invoices_values = dict()
        for representative in docs:
            # retrieve all invoices (from companies and childs) to which current representative is linked
            commissionned_invoices = self.env['account.move']
            if representative.represented_company_ids:
                commissionned_invoices |= representative.represented_company_ids.mapped('invoice_ids').filtered(
                    lambda inv: inv.state not in ['draft', 'cancel'])
                commissionned_invoices |= representative.represented_company_ids.mapped('child_ids.invoice_ids').filtered(
                    lambda inv: inv.state not in ['draft', 'cancel'])

            # create a dictionary with untaxed amount without shipping costs and last payment date for each invoice
            delivery_products = self.env['delivery.carrier'].search([]).mapped('product_id')
            invoices_data = dict()
            for invoice in commissionned_invoices:
                payment = self.env['account.payment'].search([('invoice_ids', '=', invoice.id)])
                last_payment_date = max(payment.mapped('payment_date')) if payment else False
                invoice_lines = invoice.mapped('invoice_line_ids').filtered(lambda line: line.product_id not in delivery_products)
                untaxed_total = sum(invoice_lines.mapped('price_subtotal'))
                invoices_data[invoice.id] = {'last_payment': last_payment_date, 'untaxed_total': untaxed_total}

            commercial_partners = commissionned_invoices.mapped('partner_id.commercial_partner_id')
            invoices = commissionned_invoices.filtered(lambda inv:
                                                       inv.amount_residual == 0.0 and invoices_data[inv.id].get('last_payment')
                                                       and start_date <= invoices_data[inv.id]['last_payment'] <= end_date)
            percentage = representative.commission_percentage
            invoices_values[representative.id] = {
                'total_commissions': 0.0,
                'total_invoiced': sum([invoices_data[inv.id].get('untaxed_total', 0.0) for inv in invoices]),
                'commission_percentage': percentage,
                'invoices': []
            }
            for partner in commercial_partners.sorted(key=lambda p: p.name):
                partner_invoices = invoices.filtered(lambda inv: inv.partner_id.commercial_partner_id == partner)
                lines = [{
                    'order_no': ', '.join([order.name for order in inv.invoice_line_ids.mapped('sale_line_ids.order_id')]),
                    'invoice_no': inv.name,
                    'invoice_date': invoices_data[inv.id].get('last_payment', ''),
                    'invoice_total': invoices_data[inv.id].get('untaxed_total', 0.0),
                    'commission_amount': float_round(invoices_data[inv.id].get('untaxed_total', 0.0) * percentage, precision_rounding=0.01, rounding_method='HALF-UP'),
                    'due_date': inv.invoice_date_due
                } for inv in partner_invoices]
                invoices_values[representative.id]['invoices'].append({
                    'name': partner.name,
                    'ref': partner.ref,
                    'total': sum([invoices_data[inv.id].get('untaxed_total', 0.0) for inv in partner_invoices]),
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
