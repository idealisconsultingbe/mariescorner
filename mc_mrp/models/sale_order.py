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
    ], string='Manufacturing Status', readonly=True, copy=False, index=True, tracking=True, store=True, compute='_compute_manufacturing_state',
        help="None: SO is not confirmed or SO does not contain producible products\n"
             "To Produce: SO is confirmed but has not been send to the manufacturing\n"
             "In Manufacturing: SO is confirmed and has been send to the manufacturing but some MO are not confirmed yet\n"
             "Confirmed: SO is confirmed and all its MO are confirmed\n"
             "Done: SO is confirmed and all its MO are done or cancelled")

    @api.depends('order_line.sales_lot_id.production_ids.state', 'state')
    def _compute_manufacturing_state(self):
        """
        Manuf State = None: for every SO that are in draft or sent (There are nothing to produce)
                            for every SO that do not contain sale lots
        Manuf State = To Produce: SO is confirmed but no Manufacturing Order have been created for this SO.
        Manuf State = In Manufacturing: SO is confirmed, Manufacturing Order Have been created but some of them have not been confirmed.
        Manuf State = Confirmed: SO is confirmed and all its Manufacturing Order have been confirmed.
        Manuf State = Done: SO is confirmed and all its Manufacturing Order have been confirmed or cancelled.
        :return: The manufacturing state of the SO
        """
        # Manually track "state" and "reservation_state" since tracking doesn't work with computed
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
            elif order.state in ['sale', 'done']:
                manuf_orders = sales_lots.mapped('production_ids')
                if not manuf_orders:
                    order.manufacturing_state = 'to_produce'
                elif all([mo.state in ['done', 'cancel'] for mo in manuf_orders]):
                    order.manufacturing_state = 'done'
                elif all([mo.state != 'draft' for mo in manuf_orders]):
                    order.manufacturing_state = 'confirmed'
                else:
                    order.manufacturing_state = 'in_manufacturing'
            else:
                order.manufacturing_state = 'none'

        if tracking and initial_values:
            self.message_track(self.fields_get(["manufacturing_state"]), initial_values)

    def _action_confirm(self):
        """ Overridden Method
            Add context info to skip MO confirmation if this sale order creates a MO
        """
        self = self.with_context(skip_mo_confirmation=True)
        return super(SaleOrder, self)._action_confirm()
