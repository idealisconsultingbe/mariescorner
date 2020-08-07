# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    po_state = fields.Selection([
        ('none', 'None'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Purchase Order Status', compute='_compute_po_state')

    def _compute_po_state(self):
        for order in self:
            purchase_order = self._get_purchase_order()
            if not purchase_order or len(purchase_order) > 1:
                order.po_state = 'none'
            else:
                order.po_state = purchase_order.state

    def _action_confirm(self):
        automatic_lot_enabled = self.user_has_groups('mc_sale.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        if production_lot_enabled:
            for order in self:
                for line in order.order_line.filtered(lambda l: l.has_tracking and not l.sales_lot_id):
                    name = self.env['ir.sequence'].next_by_code('stock.production.sales.lot') if automatic_lot_enabled else line.sales_lot_number
                    sales_lot_id = self.env['stock.production.sales.lot'].create({'name': name, 'product_id': line.product_id.id})
                    line.update({'sales_lot_id': sales_lot_id.id, 'sales_lot_number': name})
        return super(SaleOrder, self)._action_confirm()

    def action_confirm_purchase_order(self):
        self.ensure_one()
        purchase_order_id = self._get_purchase_order()
        if not purchase_order_id:
            raise UserError(_("There is no purchase order to confirm for this sale."))
        elif len(purchase_order_id) > 1:
            raise UserError(_('There is more than one purchase order to confirm for this sale.'))
        else:
            purchase_order_id.button_confirm()

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
