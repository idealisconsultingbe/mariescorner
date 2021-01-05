# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
