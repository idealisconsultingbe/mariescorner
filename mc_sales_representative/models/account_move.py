# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    last_payment_date = fields.Date(string='Last Payment Date', compute='_compute_last_payment_date')

    def _compute_last_payment_date(self):
        for invoice in self:
            payment = self.env['account.payment'].search([('invoice_ids', '=', invoice.id)])
            invoice.last_payment_date = max(payment.mapped('payment_date')) if payment else False