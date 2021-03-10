# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools import float_round


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_length_uom(self):
        return self.get_length_uom_name()

    tailor_made = fields.Boolean(string='Is Tailor Made', default=False)
    linear_length = fields.Float('Linear Length', digits='Product Unit of Measure', default=0.0, help='Quantity of fabric required to upholster furniture')
    length_uom_name = fields.Char(string='Length UoM Label', compute='_compute_length_uom_name', default=_default_length_uom, store=True)
    description_line_ids = fields.One2many('product.configurator.description.line', 'product_tmpl_id', string='Description Lines', help='Configuration of product short description. '
                                                                                                                                        'Helps to configure short description of product displayed on sale orders lines and purchase orders lines.')

    @api.model_create_multi
    def create(self, vals_list):
        """
        Add the hs_code on product variants
        """
        templates = super(ProductTemplate, self).create(vals_list)

        # This is needed to set given values to first variant after creation
        for template, vals in zip(templates, vals_list):
            related_vals = {}
            if vals.get('hs_code'):
                related_vals['hs_code'] = vals['hs_code']
            if related_vals and len(template.product_variant_ids) == 1:
                template.product_variant_ids.write(related_vals)
        return templates

    def write(self, values):
        """
        Update the hs code also on product variants.
        """
        if values.get('hs_code'):
            for product in self:
                if len(product.product_variant_ids) == 1:
                    self.mapped('product_variant_ids').write({'hs_code': values['hs_code']})
        return super(ProductTemplate, self).write(values)

    def _compute_length_uom_name(self):
        for template in self:
            template.length_uom_name = self.get_length_uom_name()

    @api.onchange('tailor_made')
    def onchange_tailor_made(self):
        """
        A product that is tailor-made should not have attribute with an extra price. We then check the flag manual price in order to prevent
        Odoo from computing automatically extra price. The price of a tailor-made product is complex to compute since a lot of variables are envolved.
        Sales price of tailor-made products should be computed manually by the seller.
        """
        product_template_attribute_values = self.env['product.template.attribute.value'].search([('product_tmpl_id', 'in', self.ids)])
        if product_template_attribute_values:
            if self.tailor_made:
                product_template_attribute_values.write({'is_manual_price_extra': True})
            else:
                product_template_attribute_values.write({'is_manual_price_extra': False})

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        """
        When we duplicate a product template we also duplicate its description_line_ids.
        """
        self.ensure_one()
        res = super(ProductTemplate, self).copy(default=default)
        for line in self.description_line_ids:
            new_line = self.env['product.configurator.description.line'].create({'product_tmpl_id': res.id})
            for value in line.value_ids:
                self.env['product.configurator.description.line.value'].create(
                    {'description_line_id': new_line.id,
                     'type': value.type,
                     'attribute_id': value.attribute_id.id if value.attribute_id else False,
                     'text': value.text})
        return res

    def get_product_configurable_description(self, product_custom_attribute_values, product_no_variant_attribute_values, partner, product_qty=1.0, product_variant=False, display_custom=False):
        """
        :param product_custom_attribute_values: Recordset of product.attribute.custom.value
        :param product_no_variant_attribute_values: Recordset of product.template.attribute.value
        :param partner: Record of res.partner
        :param product_qty: A float
        :param product_variant: Record of product.product
        :param display_custom: True if you want to display custom values of linear attributes.
        Return short description with product attributes flagged accordingly and description lines set on the product.template
        """
        self.ensure_one()
        product_description = product_variant.get_product_multiline_description_sale() if product_variant and product_variant.get_product_multiline_description_sale() else ""
        product_configuration = formatted_product_configuration = ""
        if product_custom_attribute_values and product_no_variant_attribute_values:
            custom_ptavs = product_custom_attribute_values.custom_product_template_attribute_value_id
            no_variant_ptavs = product_no_variant_attribute_values._origin
            desc_line_ids = self.description_line_ids
            desc_line_attributes = self.env['product.attribute']
            if desc_line_ids:
                pacvs = product_custom_attribute_values
                no_custom_ptavs = no_variant_ptavs - custom_ptavs
                desc_line_attributes = desc_line_ids.mapped('value_ids').mapped('attribute_id')
                for line in desc_line_ids:
                    formatted_product_values = []
                    for desc_value in line.value_ids:
                        if desc_value.type == 'text':
                            formatted_product_values.append(desc_value.with_context(lang=partner.lang).text)
                        else:
                            if desc_value.attribute_id in pacvs.mapped('custom_product_template_attribute_value_id').mapped('attribute_id'):
                                # We do not display none value neither attribute that do not match a description line value.
                                for pacv in pacvs.filtered(lambda p: p.custom_product_template_attribute_value_id.attribute_id == desc_value.attribute_id and not p.custom_product_template_attribute_value_id.product_attribute_value_id.is_none_value):
                                    attribute_value_name = pacv.with_context(lang=partner.lang).custom_product_template_attribute_value_id.name
                                    if pacv.custom_value and pacv.custom_product_template_attribute_value_id.attribute_id.has_linear_price:
                                        if display_custom:
                                            custom_value = float(pacv.custom_value)
                                            custom_value = float_round(custom_value * (product_qty or 1.0), precision_digits=2)
                                            formatted_text = '{}m / {}'.format(custom_value, attribute_value_name)
                                        else:
                                            formatted_text = attribute_value_name
                                        formatted_product_values.append(formatted_text)
                                    else:
                                        if desc_value.text:
                                            formatted_product_values.append("{} {}".format(desc_value.with_context(lang=partner.lang).text, attribute_value_name))
                                        else:
                                            formatted_product_values.append(attribute_value_name)
                            elif desc_value.attribute_id in no_custom_ptavs.mapped('attribute_id'):
                                # We do not display none value neither attribute that do not match a description line value.
                                for ptav in no_custom_ptavs.filtered(lambda p: p.attribute_id == desc_value.attribute_id and not p.product_attribute_value_id.is_none_value):
                                    if desc_value.text:
                                        formatted_product_values.append("{} {}".format(desc_value.with_context(lang=partner.lang).text, ptav.with_context(lang=partner.lang).name))
                                    else:
                                        formatted_product_values.append(ptav.with_context(lang=partner.lang).name)
                    if not formatted_product_configuration and formatted_product_values:
                        formatted_product_configuration = ' '.join(formatted_product_values)
                    elif formatted_product_values:
                        formatted_product_configuration = '{}{}{}'.format(formatted_product_configuration, '\n', ' '.join(formatted_product_values))

            # display the no_variant attributes, except those that are also
            # displayed by a custom (avoid duplicate description)
            # select only those that should be displayed in short description
            for ptav in (no_variant_ptavs - custom_ptavs).filtered(lambda p: p.attribute_id.display_short_description and p.attribute_id not in desc_line_attributes):
                product_configuration += '\n' + ptav.with_context(lang=partner.lang).display_name

            # display the is_custom values
            # select only those that should be displayed in short description
            for pacv in product_custom_attribute_values.filtered(lambda p: p.custom_product_template_attribute_value_id.attribute_id.display_short_description and p.custom_product_template_attribute_value_id.attribute_id not in desc_line_attributes):
                product_configuration += '\n' + pacv.with_context(lang=partner.lang).display_name

        return '{}\n{}{}'.format(product_description, formatted_product_configuration, product_configuration)


    @api.model
    def get_length_uom_name(self):
        """ Retrieve reference uom name for length measures.
        It is possible to change this easily to use uom from ir.config.parameter for example """
        uom = self.env.ref('uom.product_uom_meter', False) or self.env['uom.uom'].search(
            [('measure_type', '=', 'length'), ('uom_type', '=', 'reference')], limit=1)
        return uom.name
