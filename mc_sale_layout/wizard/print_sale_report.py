# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, _


class PrintSaleReport(models.TransientModel):
    _name = 'print.sale.report'
    _description = 'Print Sale Report With Different Company Header/Footer'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    action_report_id = fields.Many2one('ir.actions.report', string='Report', required=True, domain="[('model', '=', 'sale.order'), ('report_type', '=', 'qweb-pdf')]")

    def action_print(self):
        self.ensure_one()
        filename = '[{}]{} - {}.pdf'.format(self.company_id.name, self.sale_order_id.name, self.sale_order_id.partner_id.name)
        data = dict(company=self.company_id)
        pdf, ext = self.action_report_id.render_qweb_pdf(self.sale_order_id.id, data)
        self.sale_order_id.message_post(body=(_('{} has been generated with {} header/footer.')).format(self.action_report_id.name, self.company_id.name), attachments=[(filename, pdf)])


