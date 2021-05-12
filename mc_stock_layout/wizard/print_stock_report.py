# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
import base64
from odoo import fields, models, _


class PrintStockReport(models.TransientModel):
    _name = 'print.stock.report'
    _description = 'Print Stock Report With Different Company Header/Footer'

    picking_id = fields.Many2one('stock.picking', string='Picking', readonly=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    action_report_id = fields.Many2one('ir.actions.report', string='Report', required=True, domain="[('model', '=', 'stock.picking'), ('report_type', '=', 'qweb-pdf')]")

    def action_print(self):
        self.ensure_one()
        filename = '[{}]{} - {}.pdf'.format(self.company_id.name, self.picking_id.name, self.picking_id.partner_id.name)
        data = dict(company=self.company_id)
        pdf, ext = self.action_report_id.render_qweb_pdf(self.picking_id.id, data)

        attachment = self.env['ir.attachment'].create({
                            'name': filename,
                            'type': 'binary',
                            'datas': base64.encodestring(pdf),
                            'res_model': self.picking_id._name,
                            'res_id': self.picking_id.id
                        })
        self.picking_id.message_post(body=(_('{} has been generated with {} header/footer.')).format(self.action_report_id.name, self.company_id.name), attachment_ids=[attachment.id])
        return {
                    'type': 'ir.actions.act_url',
                    'url': '/web/content/{}?download=true'.format(attachment.id),
                    'target': 'self',
                }
