# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmation_done = fields.Boolean(help='Used just for UI purposes in order to hide button if confirmation is done')

    def action_confirm_purchase_order(self):
        self.ensure_one()
        purchase_order_id = self._get_purchase_order()
        if not purchase_order_id:
            raise UserError(_("There is no purchase order to confirm for this sale."))
        elif len(purchase_order_id) > 1:
            raise UserError(_('There is more than one purchase order to confirm for this sale.'))
        else:
            purchase_order_id.button_confirm()
            self.confirmation_done = True

    def _get_purchase_order(self):
        """
        Retrieve purchase order(s) if there is a MTO product with buy route
        """
        self.ensure_one()
        purchase_order_ids = self.env['purchase.order']
        for line in self.order_line:
            if line.move_ids:
                move = line.move_ids[0]
                if move.created_purchase_line_id:
                    purchase_order_ids += move.created_purchase_line_id.order_id
                elif move.move_orig_ids and move.move_orig_ids[0].purchase_line_id:
                    purchase_order_ids += move.move_orig_ids[0].purchase_line_id.order_id
        return purchase_order_ids


