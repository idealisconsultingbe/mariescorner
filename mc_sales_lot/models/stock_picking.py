# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class Picking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        """
        Overridden method

        Create an entry log if
            - there is at least one move line bound to a sales lot
            - AND it is an intercompany transfer OR a customer delivery
        """
        res = super(Picking, self).action_done()
        companies = self.env['res.company'].search([]).read(['partner_id'])
        user = self.env.user
        model = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
        record = self.env.context.get('active_id')
        for line in self.move_line_ids.filtered(lambda l: l.sales_lot_id):
            if self.picking_type_code == 'incoming' and self.partner_id.id in [company['partner_id'][0] for company in companies]:
                msg = _('The lot {} have been received by {}').format(line.lot_id.name, self.company_id.name)
                line.sales_lot_id.create_log(msg, user=user, model=model, record=record)
            elif self.picking_type_code == 'outgoing' and self.partner_id.id in [company['partner_id'][0] for company in companies]:
                msg = _('The lot {} is on its way towards {} warehouse').format(line.lot_id.name, self.partner_id.name)
                line.sales_lot_id.create_log(msg, user=user, model=model, record=record)
            elif self.picking_type_code == 'outgoing':
                msg = _('The lot {} have been delivered to customer {}').format(line.lot_id.name, self.partner_id.name)
                line.sales_lot_id.create_log(msg, user=user, model=model, record=record)
        return res

        # if self.picking_type_code == 'outgoing':
        #     companies = self.env['res.company'].search([]).read(['partner_id'])
        #     if self.partner_id.id in [company['partner_id'][0] for company in companies]:
        #         for line in self.move_line_ids:
        #             if line.sales_lot_id:
        #                 msg = _('The lot {} is on its way towards {} warehouse').format(line.lot_id.name, self.partner_id.name)
        #                 model = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
        #                 line.sales_lot_id.create_log(msg, user=self.env.user, model=model, record=self.env.context.get('active_id'))
        #     else:
        #         for line in self.move_line_ids:
        #             if line.sales_lot_id:
        #                 msg = _('The lot {} have been delivered to customer {}').format(line.lot_id.name, self.partner_id.name)
        #                 model = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
        #                 line.sales_lot_id.create_log(msg, user=self.env.user, model=model, record=self.env.context.get('active_id'))
        # if self.picking_type_code == 'incoming':
        #     for line in self.move_line_ids:
        #         if line.sales_lot_id:
        #             msg = _('The lot {} have been received by {}').format(line.lot_id.name, self.company_id.name)
        #             model = self.env['ir.model'].search([('model', '=', self.env.context.get('active_model'))])
        #             line.sales_lot_id.create_log(msg, user=self.env.user, model=model, record=self.env.context.get('active_id'))
        # return res
