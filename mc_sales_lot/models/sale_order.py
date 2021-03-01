# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    mandatory_date = fields.Date(string='Mandatory Date', states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]}, copy=False, readonly=True)
    editable_mandatory_date = fields.Boolean(string='Editable Mandatory Date', compute='_compute_editable_mandatory_date', help='Used in UI. Prevent user to edit mandatory date if he is not member of the right group.')

    def _compute_editable_mandatory_date(self):
        """
        Check if user has rights to edit mandatory date. If not, field is in readonly mode.
        This prevents user to modify mandatory date and trying to save it.
        """
        edit_mandatory_date_group = self.env.user.has_group('mc_sales_lot.group_edit_mandatory_date')
        for order in self:
            order.editable_mandatory_date = edit_mandatory_date_group

    def _action_confirm(self):
        """ Overridden Method
            Create Stock Production Manufacturing Number at order confirmation and update order lines accordingly.
            Manufacturing Numbers may be created automatically or manually according to configuration settings.
        """
        automatic_lot_enabled = self.user_has_groups('mc_sales_lot.group_automatic_sales_lot')
        production_lot_enabled = self.user_has_groups('stock.group_production_lot')
        if production_lot_enabled and automatic_lot_enabled:
            for order in self:
                for line in order.order_line.filtered(lambda l: l.has_tracking and not l.sales_lot_id and l.product_id and l.product_id.sales_lot_activated):
                    values = line._prepare_sales_lot_id()
                    sales_lot_id = self.env['stock.production.sales.lot'].create(values)
                    line.update({'sales_lot_id': sales_lot_id.id})
        return super(SaleOrder, self)._action_confirm()
