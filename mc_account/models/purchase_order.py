# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_invoice(self):
        """
        Overridden method
        Display custom wizard to choose whether multi-company transactional purchase lines should be billed or not
        This wizard is only displayed if invoices of multi-company transactions are synchronized and user clicks on 'create invoice' button on purchase order
        """
        if self.env.context.get('show_wizard_bill_lines_sync', False) and self.user_has_groups('mc_account.group_invoices_synchronization'):
            action = self.env.ref('mc_account.action_create_vendor_bill')
            result = action.read()[0]
            result['context'] = {'default_purchase_order_id': self.id}
            return result
        else:
            return super(PurchaseOrder, self).action_view_invoice()
