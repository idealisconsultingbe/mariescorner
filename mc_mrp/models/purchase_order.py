# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    to_be_confirmed = fields.Boolean(string='To Be Confirmed')

    def button_approve(self, force=False):
        """
        During the purchase order validation automatically send an email to external suppliers if some products use manufacturing numbers.
        """
        result = super(PurchaseOrder, self).button_approve(force=force)
        for order in self:
            lines = order.order_line.filtered(lambda l: l.sales_lot_id.supplier_type == 'external')
            if lines:
                template = self.env.ref('mc_mrp.mail_template_purchase_production_approval', raise_if_not_found=True)
                production_sheet = self.env.ref('mc_sales_lot.action_report_saleslot')
                manufacturing_number_labels = self.env.ref('mc_sales_lot.action_report_saleslot_label')
                reports = production_sheet | manufacturing_number_labels
                attachments = lines.mapped('sales_lot_id').get_sales_lot_attachment(reports)
                attachments_data = []
                for sales_lot_id in attachments:
                    attachments_data += attachments[sales_lot_id]
                attachment_values =  [(0, 0, {'name': attachment[0],
                                             'mimetype': 'application/pdf',
                                             'datas': attachment[1]}) for attachment in attachments_data]
                email_values = {'attachment_ids': attachment_values}
                template.send_mail(order.id, email_values=email_values, force_send=True)
        return result

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        """ Overridden Method

            Generate the Sales Order Line values from the PO line.
            Add Stock product attribute values to SO Line values.
            :param line : the origin Purchase Order Line
            :rtype line : purchase.order.line record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param sale_id : the id of the SO
        """
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        if line.product_no_variant_attribute_value_ids or line.product_custom_attribute_value_ids:
            res.update({
                'name': line.name,
                'product_no_variant_attribute_value_ids': [(6, 0, line.product_no_variant_attribute_value_ids.ids)],
                'product_custom_attribute_value_ids': [(6, 0, line.product_custom_attribute_value_ids.ids)],
                'comment': line.comment,
            })
        res['trigger_product_id_onchange'] = True # Used to trigger the product_id_onchange in the create method!
        return res
