# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

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
    manufacturing_state = fields.Selection([
        ('none', 'None'),
        ('to_produce', 'To Produce'),
        ('in_manufacturing', 'In Manufacturing'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Manufacturing Status', readonly=True, copy=False, index=True, tracking=True, store=True, compute='_compute_manufacturing_state',
        help="None: SO is not confirmed or SO does not contain producible products\n"
             "To Produce: at least one manufacturing number is in state 'To Produce'\n"
             "In Manufacturing: no manufacturing number is in state 'To Produce' and at least one is in state 'In Manufacturing'\n"
             "Confirmed: all manufacturing numbers are confirmed or done\n"
             "Done: all manufacturing numbers are done\n"
             "Cancelled: at least one manufacturing number is cancelled")

    @api.depends('order_line.sales_lot_id.manufacturing_state')
    def _compute_manufacturing_state(self):
        """
        Compute manufacturing state of each sale order
            Manuf State = None: for every SO that are in draft or sent (There are nothing to produce)
                                for every SO that do not contain sale lots
            Manuf State = To Produce: at least one manufacturing number is in state 'To Produce'.
            Manuf State = In Manufacturing: no manufacturing number is in state 'To Produce' and at least one is in state 'In Manufacturing'.
            Manuf State = Confirmed: all manufacturing numbers are confirmed or done.
            Manuf State = Done: all manufacturing numbers are done.
            Manuf State = Cancelled: at least one manufacturing number is cancelled.
        """
        # Manually track "manufacturing_state" since tracking doesn't work with computed
        # fields.
        tracking = not self._context.get("mail_notrack") and not self._context.get("tracking_disable")
        initial_values = {}
        if tracking:
            initial_values = dict(
                (order.id, {"manufacturing_state": order.manufacturing_state})
                for order in self
            )

        for order in self:
            sales_lots = order.mapped('order_line.sales_lot_id')
            if not sales_lots or order.state in ['draft', 'sent']:
                order.manufacturing_state = 'none'
            elif sales_lots:
                sales_lots_status = sales_lots.mapped('manufacturing_state')
                if any([status == 'cancel' for status in sales_lots_status]):
                    order.manufacturing_state = 'cancel'
                elif any([status == 'to_produce' for status in sales_lots_status]):
                    order.manufacturing_state = 'to_produce'
                elif any([status == 'in_manufacturing' for status in sales_lots_status]):
                    order.manufacturing_state = 'in_manufacturing'
                elif all([status == 'done' for status in sales_lots_status]):
                    order.manufacturing_state = 'done'
                elif all([status in ['confirmed', 'done'] for status in sales_lots_status]):
                    order.manufacturing_state = 'confirmed'
                else:
                    order.manufacturing_state = 'none'

        if tracking and initial_values:
            self.message_track(self.fields_get(["manufacturing_state"]), initial_values)

    def _action_confirm(self):
        """
        Overridden Method
        Add context info to skip MO confirmation if this sale order creates a MO
        """
        self = self.with_context(skip_mo_confirmation=True)
        return super(SaleOrder, self)._action_confirm()

    def _compute_po_state(self):
        """ Retrieve Purchase Order Status from related purchase order """
        for order in self:
            purchase_order = self._get_purchase_order()
            if not purchase_order or len(purchase_order) > 1:
                order.po_state = 'none'
            else:
                order.po_state = purchase_order.state

    def _get_purchase_order(self):
        """ Retrieve purchase order(s) if there is a MTO product with buy route """
        self.ensure_one()
        purchase_order_ids = self.env['purchase.order']
        for line in self.order_line:
            purchase_order_lines = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)])
            if purchase_order_lines:
                purchase_order_ids = purchase_order_lines.mapped('order_id')
            if line.move_ids:
                move = line.move_ids[0]
                purchase_order_line = move._get_purchase_line_id()
                if purchase_order_line:
                    purchase_order_ids |= purchase_order_line.order_id
        return purchase_order_ids

    def action_confirm_purchase_order(self):
        """ Ensure that there is only one purchase order related to this sale order and confirm it """
        self.ensure_one()
        purchase_order_id = self._get_purchase_order()
        if not purchase_order_id:
            raise UserError(_("There is no purchase order to confirm for this sale."))
        elif len(purchase_order_id) > 1:
            raise UserError(_('There is more than one purchase order to confirm for this sale.'))
        else:
            external_sales_lot = self.order_line.mapped('sales_lot_id').filtered(lambda sl: sl.supplier_type == 'external')
            if external_sales_lot:
                external_sales_lot.write({'external_state': 'in_manufacturing'})
            purchase_order_id.button_confirm()
