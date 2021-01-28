# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from .tools import to_float
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

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False, **kw):
        """ Overridden method used in product configurator
            If configurator uses custom values then compute extra prices according to them
            (attribute custom value * price unit of attribute value)
        """
        self.ensure_one()
        res = super(ProductTemplate, self)._get_combination_info(combination, product_id, add_qty, pricelist, parent_combination, only_template)

        if kw.get('custom_values'):
            # dict of quantities
            custom_quantities = {value['custom_product_template_attribute_value_id']: to_float(value['custom_value']) for value in kw.get('custom_values')}

            # standard
            context = dict(self.env.context, quantity=self.env.context.get('quantity', add_qty), pricelist=pricelist.id if pricelist else False)
            product_template = self.with_context(context)
            product = product_template.env['product.product'].browse(res.get('product_id'))
            combination = combination or product_template.env['product.template.attribute.value']
            if not product_id and not combination and not only_template:
                combination = product_template._get_first_possible_combination(parent_combination)

            # retrieve product template attribute values bound to custom values in order to remove them from price extra computation
            custom_combination = product_template.env['product.template.attribute.value'].browse([value['custom_product_template_attribute_value_id'] for value in kw.get('custom_values')])
            # Keeps only custom attribute values linked to an attribute marked as linear price and for which the manual extra price is not activated.
            custom_combination = custom_combination.filtered(lambda x: not x.is_manual_price_extra and x.attribute_id.has_linear_price)
            combination = combination - custom_combination

            if product:
                no_variant_attributes_price_extra = [
                    ptav.price_extra for ptav in combination.filtered(
                        lambda ptav:
                        ptav.price_extra and
                        ptav not in product.product_template_attribute_value_ids
                    )
                ]
                # compute correct extra prices of custom attribute values
                no_variant_attributes_price_extra += [
                    ptav.product_attribute_value_id.unit_price * custom_quantities[ptav.id] for ptav in custom_combination.filtered(
                        lambda ptav:
                        ptav.product_attribute_value_id.unit_price and
                        ptav not in product.product_template_attribute_value_ids
                    )
                ]
                # standard
                if no_variant_attributes_price_extra:
                    product = product.with_context(
                        no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
                    )
                list_price = product.price_compute('list_price')[product.id]
                price = product.price if pricelist else list_price
            else:
                # FIXME: is this necessary ? We apply the same logic on product template
                current_attributes_price_extra = [v.price_extra or 0.0 for v in combination]
                current_attributes_price_extra += [v.product_attribute_value_id.unit_price * custom_quantities[v.id] for v in custom_combination]
                # standard
                product_template = product_template.with_context(current_attributes_price_extra=current_attributes_price_extra)
                list_price = product_template.price_compute('list_price')[product_template.id]
                price = product_template.price if pricelist else list_price

            # standard
            if pricelist and pricelist.currency_id != product_template.currency_id:
                list_price = product_template.currency_id._convert(
                    list_price, pricelist.currency_id, product_template._get_current_company(pricelist=pricelist),
                    fields.Date.today()
                )
            # standard
            price_without_discount = list_price if pricelist and pricelist.discount_policy == 'without_discount' else price
            has_discounted_price = (pricelist or product_template).currency_id.compare_amounts(price_without_discount,price) == 1
            res.update({'price': price, 'list_price': list_price, 'has_discounted_price': has_discounted_price})

        return res
