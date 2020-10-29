# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        """
        Overridden method

        Create an entry log if
            - there is at least one move line bound to a manufacturing number
            - AND it is an intercompany transfer OR a customer delivery
        """
        def is_intercompany(partner, companies):
            """ inner function that defines if partner is part of a company """
            if partner.id in [company['partner_id'][0] for company in companies]:
                return True
            elif partner.parent_id:
                return is_intercompany(partner.parent_id, companies)
            else:
                return False

        res = super(Picking, self).action_done()
        companies = self.env['res.company'].search([]).read(['partner_id'])
        user = self.env.user
        model = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
        record = self.env.context.get('active_id')
        for line in self.move_line_ids.filtered(lambda l: l.sales_lot_id):
            if self.picking_type_code == 'incoming' and is_intercompany(self.partner_id, companies):
                name = {'no_lang': _('Receipt OK'), 'en_US': 'Receipt OK', 'fr_BE': 'Réception OK'}
                msg = {
                    'no_lang': _('The SN {} has been received by {}').format(line.lot_id.name, self.company_id.partner_id.name_get()[0][1]),
                    'en_US': 'The SN {} has been received by {}'.format(line.lot_id.name, self.company_id.partner_id.name_get()[0][1]),
                    'fr_BE': 'Le numéro de série {} a été réceptionné par {}'.format(line.lot_id.name, self.company_id.partner_id.name_get()[0][1]),
                }
                line.sales_lot_id.create_log(name, msg, user=user, model=model, record=record)
            elif self.picking_type_code == 'outgoing' and is_intercompany(self.partner_id, companies):
                name = {'no_lang': _('Internal Delivery OK'), 'en_US': 'Internal Delivery OK', 'fr_BE': 'Livraison Interne OK'}
                msg = {
                    'no_lang': _('The SN {} is on its way towards {} warehouse').format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                    'en_US': 'The SN {} is on its way towards {} warehouse'.format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                    'fr_BE': 'Le numéro de série {} est en chemin vers l\'entrepôt de {}'.format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                }
                line.sales_lot_id.create_log(name, msg, user=user, model=model, record=record)
            elif self.picking_type_code == 'outgoing':
                name = {'no_lang': _('Delivery OK'), 'en_US': 'Delivery OK', 'fr_BE': 'Livraison OK'}
                msg = {
                    'no_lang': _('The SN {} has been delivered to customer {}').format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                    'en_US': 'The SN {} has been delivered to customer {}'.format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                    'fr_BE': 'Le numéro de série {} a été livré au client {}'.format(line.lot_id.name, self.partner_id.name_get()[0][1]),
                }
                line.sales_lot_id.create_log(name, msg, user=user, model=model, record=record)
        return res
