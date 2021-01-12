# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    is_sales_representative = fields.Boolean(string='Is Sales Representative')
    sales_representative_id = fields.Many2one('res.partner', string='Sales Representative', domain=[('type', '=', 'contact'), ('is_sales_representative', '=', True)])
    represented_company_ids = fields.One2many('res.partner', 'sales_representative_id', string='Represented Companies')
    commission_percentage = fields.Float(string='Commission', default=0.1)
    representative_ref = fields.Char(string='Representative Reference')

    @api.onchange('type')
    def _onchange_type(self):
        if self.type != 'contact':
            self.is_sales_representative = False

    @api.onchange('company_type')
    def _onchange_company_type(self):
        if self.company_type != 'person':
            self.is_sales_representative = False

    def print_commissions_report_action(self, start_date=None, end_date=None):
        """
        Print commissions report
        If at least one date is not set, then print report of last month
        """
        if not start_date or not end_date:
            start_date = datetime.date.today().replace(day=1) + relativedelta(months=-1)
            end_date = datetime.date.today().replace(day=1) + relativedelta(days=-1)
        representatives = self.filtered(lambda partner: partner.is_sales_representative)
        data = {
            'start_date': start_date.strftime('%d/%m/%y'),
            'end_date': end_date.strftime('%d/%m/%y'),
            'representative_ids': representatives.ids,
        }
        return self.env.ref('mc_sales_representative.sales_commissions').report_action(representatives, data=data)

    def _get_report_base_filename(self):
        """ Return report name according to dates set in context """
        name = '{}_commissions_report'.format((datetime.date.today() + relativedelta(months=-1)).strftime("%m-%Y"))
        return name
