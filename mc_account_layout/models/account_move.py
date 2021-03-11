# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_bank_id = fields.Many2one('res.partner.bank', string='Bank Account for Payment', compute='_compute_payment_bank_id',
                                      store=True, check_company=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                      help='Bank account used by customer for payment')

    @api.depends('partner_id.country_id', 'company_id.partner_id.bank_ids', 'company_id.partner_id.country_id')
    def _compute_payment_bank_id(self):
        """
        Compute account used for customer payments

        Use the first available company bank account from the same country than customer
        If not found/applicable, use the first available company bank account from the same country than company
        If not found/applicable, use the first available company bank account set on company partner
        else False
        """
        for order in self:
            payment_bank = False
            banks = False
            if order.partner_id.country_id:
                banks = self.env['res.bank'].search([('country', '=', order.partner_id.country_id.id)])
            if not banks and order.company_id.partner_id.country_id:
                banks = self.env['res.bank'].search([('country', '=', order.company_id.partner_id.country_id.id)])

            if banks:
                payment_bank = self.env['res.partner.bank'].search([('company_id', '=', order.company_id.id), ('partner_id', '=', order.company_id.partner_id.id), ('bank_id', 'in', banks.ids)], limit=1, order='sequence asc')
            if not payment_bank:
                payment_bank = self.env['res.partner.bank'].search([('company_id', '=', order.company_id.id), ('partner_id', '=', order.company_id.partner_id.id)], limit=1, order='sequence asc')
            order.payment_bank_id = payment_bank
