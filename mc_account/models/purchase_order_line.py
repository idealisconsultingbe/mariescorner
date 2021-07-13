# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move):
        """
        Overridden method
        If invoices of multi-company transactions are synchronized and user chooses to not create bill lines for purchase lines involved in a multi-company transaction
        then we return an empty dictionary to prevent bill line creation
        Contextual flag 'bill_synchronization' is set on wizard button to create bill
        """
        self.ensure_one()
        if self.env.context.get('bill_synchronization_type', '') == 'without_intercompany_lines' and self.user_has_groups('mc_account.group_invoices_synchronization'):
            intercompany_sale_order_line = self.sudo().env['sale.order.line'].search([('inter_company_po_line_id', '=', self.id)], limit=1)
            if intercompany_sale_order_line:
                return {}
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        res.update({'partner_ref': self.order_id.partner_ref, 'origin': self.order_id.name})
        return res
