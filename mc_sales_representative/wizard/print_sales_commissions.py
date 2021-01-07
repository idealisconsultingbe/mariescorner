# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class PrintSalesCommissions(models.TransientModel):
    _name = 'print.sales.commissions'
    _description = 'Print Commissions Report For Sales Representatives'

    partner_ids = fields.Many2many('res.partner', 'wiz_print_commissions_partner_rel', 'wiz_id', 'partner_id', string='Sales Representatives', required=True)
    start_date = fields.Date(string='Start Date', required=True, default=lambda self: datetime.date.today().replace(day=1) + relativedelta(months=-1)) # first day of previous month
    end_date = fields.Date(string='End Date', required=True, default=lambda self: datetime.date.today().replace(day=1) + relativedelta(days=-1)) # last day of previous month

    @api.onchange('start_date')
    def _onchange_start_date(self):
        """
        If user changes start_date and end_date is before this date,
        then end_date should be the end of that month
        """
        if self.start_date and (not self.end_date or self.start_date > self.end_date):
            self.end_date = self.start_date.replace(day=1) + relativedelta(months=+1, days=-1)

    @api.onchange('end_date')
    def _onchange_end_date(self):
        """
        If user changes end_date and start_date is after this date,
        then change start_date to be the first day of that month
        """
        if self.end_date and (not self.start_date or self.start_date > self.end_date):
            self.start_date = self.end_date.replace(day=1)

    @api.model
    def default_get(self, fields):
        """ Retrieve partners from active_ids """
        res = super(PrintSalesCommissions, self).default_get(fields)
        res_ids = self._context.get('active_ids')

        partners = self.env['res.partner'].browse(res_ids).filtered(lambda p: p.is_sales_representative)
        if not partners:
            partners = self.env['res.partner'].search([('is_sales_representative', '=', True)])

        res.update({'partner_ids': [(6, 0, partners.ids)]})
        return res

    def print_document_action(self):
        """
        Print commissions report for each partner
        If partners are not set, then select all sales representatives
        """
        self.ensure_one()
        if not self.partner_ids:
            self.update({'partner_ids': [(6, 0, self.env['res.partner'].search([('is_sales_representative', '=', True)]).ids)]})
        action = self.partner_ids.print_commissions_report_action(start_date=self.start_date, end_date=self.end_date)
        if action:
            return action
        else:
            return {'type': 'ir.actions.act_window_close'}
