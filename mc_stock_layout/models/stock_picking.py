# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_default_volume_uom(self):
        return self.env['product.template']._get_volume_uom_name_from_ir_config_parameter()

    volume_uom_name = fields.Char(string='Volume unit of measure label', readonly=True, default=_get_default_volume_uom)

    def _find_mail_template(self):
        # TODO select the right template according to picking state/picking type/?
        template_id = self.env['ir.model.data'].xmlid_to_res_id('mc_stock_layout.picking_availability_mail', raise_if_not_found=False)
        return template_id

    def action_confirmation_send(self):
        ''' Opens a wizard to compose a confirmation email, with relevant mail template loaded by default (with delivery slip) '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'stock.picking', self.ids[0])

        # Email to -> picking partner, user and sale representative
        partner_ids = [self.env.user.partner_id.id]
        if self.partner_id:
            partner_ids.append(self.partner_id.id)
        if self.sudo().sale_id and self.sudo().sale_id.sales_representative_id:
            partner_ids.append(self.sudo().sale_id.sales_representative_id.id)

        ctx = {
            'default_partner_ids': [(6, 0, partner_ids)],
            'default_model': 'stock.picking',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
            'force_email': True,
            'model_description': 'Delivery Order',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }