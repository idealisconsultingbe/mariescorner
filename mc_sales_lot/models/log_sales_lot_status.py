# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class LogSalesLotStatus(models.Model):
    _name = 'log.sales.lot.status'
    _description = 'Model used to log the manufacturing number status and follow its progression.'
    _order = 'date asc'

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user.id)
    date = fields.Datetime(string='Date', required=True, default=fields.Datetime.now())
    description = fields.Text(string='Description')
    name = fields.Text(string='Name', required=True)
    sales_lot_id = fields.Many2one('stock.production.sales.lot', string='Manufacturing Number', required=True)
    model_id = fields.Many2one('ir.model', string="Model")
    res_id = fields.Integer(string='Record ID')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
