# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """ Overridden Method
            Add context info to skip MO confirmation if this sale order creates a MO
        """
        self = self.with_context(skip_mo_confirmation=True)
        return super(SaleOrder, self)._action_confirm()
