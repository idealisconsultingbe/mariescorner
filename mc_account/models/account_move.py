# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def post(self):
        """
        Overridden method
        When posting an invoice:
        -   Add an analytic account on each invoice lines with a manufacturing number but no analytic account
            A new analytic account is created if it does not already exist
        -   Synchronize invoices if multi-company settings are accordingly set
        """
        # Add analytic account
        for move in self:
            for line in move.invoice_line_ids.filtered(lambda l: l.sales_lot_ids and not l.analytic_account_id):
                name = ' - '.join(line.sales_lot_ids.mapped('name'))
                analytic_account = self.env['account.analytic.account'].search([('name', '=', name)], limit=1)
                line.analytic_account_id = analytic_account if analytic_account else self.env[
                    'account.analytic.account'].create({'name': name, 'company_id': line.company_id.id})

        # Synchronize invoices between companies
        if self.user_has_groups('mc_account.group_invoices_synchronization'):
            self = self.sudo()
            params = self.env['ir.config_parameter']
            invoices_sync_origin_type = params.get_param('mc_account.invoices_sync_origin_type')
            invoices_sync_origin_company = self.env['res.company'].browse(
                int(params.get_param('mc_account.invoices_sync_origin')))
            invoices_sync_destination_company = self.env['res.company'].browse(
                int(params.get_param('mc_account.invoices_sync_destination')))
            if invoices_sync_destination_company and invoices_sync_origin_company and invoices_sync_origin_type:
                # retrieve moves that should trigger a synchronization
                account_moves = self.filtered(
                    lambda m: m.type == invoices_sync_origin_type and m.company_id == invoices_sync_origin_company)
                # handle synchronization from customer invoices to vendor bills
                # currently only this synchronization direction is handled
                if invoices_sync_origin_type == 'out_invoice':
                    # retrieve moves with multi-company transactional lines
                    moves_with_intercompany_lines = account_moves.filtered(
                        lambda m: account_moves.mapped('invoice_line_ids.sale_line_ids.inter_company_po_line_id'))
                    # if there are multi-company transactional lines and there are still quantities to invoice on purchase orders, create vendor bill
                    if moves_with_intercompany_lines and any(
                            [sale_line.qty_invoiced - sale_line.inter_company_po_line_id.qty_invoiced for sale_line in
                             moves_with_intercompany_lines.mapped('invoice_line_ids.sale_line_ids') if
                             sale_line.inter_company_po_line_id]):

                        names = [name for name in moves_with_intercompany_lines.mapped('name') if
                                 name != '/'] + moves_with_intercompany_lines.mapped(
                            'invoice_line_ids.sale_line_ids.inter_company_po_line_id.order_id.name')
                        invoice_origin = ','.join(names)
                        journal = self.env['account.journal'].search(
                            [('company_id', '=', invoices_sync_destination_company.id), ('type', '=', 'purchase')],
                            limit=1)
                        # Bill is created with a new() method in order to call onchange methods before persisting it
                        bill = self.with_context(force_company=invoices_sync_destination_company.id).env[
                            'account.move'].new({
                            'company_id': invoices_sync_destination_company.id,
                            'type': 'in_invoice',
                            'journal_id': journal.id,
                            'invoice_origin': invoice_origin,
                            'partner_id': invoices_sync_origin_company.partner_id.id,
                            'fiscal_position_id': invoices_sync_origin_company.partner_id.property_account_position_id.id
                        })
                        bill._onchange_journal()
                        bill._onchange_invoice_date()
                        bill._onchange_partner_id()

                        # create non-persisted bill lines
                        bill_invoice_lines = self.env['account.move.line']
                        for inv_line in moves_with_intercompany_lines.mapped('invoice_line_ids'):
                            for so_line in inv_line.sale_line_ids:
                                po_line = so_line.inter_company_po_line_id
                                if po_line:
                                    # lines are created if there are quantities left to bill
                                    quantity = so_line.qty_invoiced - po_line.qty_invoiced
                                    if quantity > 0:
                                        price_unit = invoices_sync_destination_company.currency_id._convert(
                                            inv_line.price_unit, bill.currency_id, invoices_sync_origin_company,
                                            bill.date, round=False)
                                        new_line = bill_invoice_lines.new(po_line._prepare_account_move_line(bill))
                                        new_line.update({
                                            'short_name': po_line.short_name,
                                            'sales_lot_ids': [
                                                (4, po_line.sales_lot_id.id, 0)] if po_line.sales_lot_id else False,
                                            'quantity': quantity,
                                            'price_unit': price_unit,
                                            'purchase_line_id': po_line.id,
                                            'discount': inv_line.discount,
                                            'name': new_line._get_computed_name(),
                                            'account_id': new_line._get_computed_account(),
                                            'tax_ids': new_line._get_computed_taxes(),
                                            'product_uom_id': new_line._get_computed_uom(),
                                            'debit': invoices_sync_destination_company.currency_id.round(
                                                price_unit * quantity),
                                        })
                                        new_line._onchange_price_subtotal()
                                        new_line._onchange_mark_recompute_taxes()
                                        bill_invoice_lines += new_line
                        # add bill lines to bill
                        bill.invoice_line_ids = bill_invoice_lines
                        bill._onchange_currency()
                        bill._onchange_invoice_line_ids()
                        # persist bill if there are bill lines
                        if bill_invoice_lines:
                            self.env['account.move'].create(bill._convert_to_write(bill._cache))
        return super(AccountMove, self).post()
