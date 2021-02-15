# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import json
from datetime import datetime

from odoo import models, http, SUPERUSER_ID
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.translate import _


class RegisterProductsForm(http.Controller):

    @http.route('/register_products', type='http', auth='public', methods=['POST'], website=True)
    def register_products(self, **kwargs):
        try:
            data = self.extract_data(request.params)
        # If we encounter an issue while extracting data, abort registration
        except Exception as e:
            warranty_error = e.args[0]
            return request.render("mc_warranty.warranty_not_activated", {'error': warranty_error})

        sale_order = request.env['sale.order'].search([('name', '=', data['form_fields']['warranty'])])
        if not sale_order:
            warranty_error = _('This warranty number %s is not correct' % data['form_fields']['warranty'])
            return request.render("mc_warranty.warranty_not_activated", {'error': warranty_error})
        elif not any(sale_order.order_line.mapped('sales_lot_id.mc_care')):
            warranty_error = _('This warranty number %s is not related to a Mc Care product' % data['form_fields']['warranty'])
            return request.render("mc_warranty.warranty_not_activated", {'error': warranty_error})
        elif sale_order.mc_care_warranty:
            warranty_error = _('This warranty number %s has already been activated' % data['form_fields']['warranty'])
            return request.render("mc_warranty.warranty_not_activated", {'error': warranty_error})

        try:
            country = request.env['res.country'].browse(data['form_fields']['country'])
            partner = request.env['res.partner'].search([('email', '=', data['form_fields']['email'])])
            if not partner:
                partner = request.env['res.partner'].create({
                    'name': '{} {}'.format(data['form_fields']['lastname'], data['form_fields']['firstname']),
                    'street': data['form_fields']['address'],
                    'city': data['form_fields']['city'],
                    'country_id': country.id if country else False,
                    'zip': data['form_fields']['zip'],
                    'email': data['form_fields']['email'],
                    'phone': data['form_fields']['phone'],
                })
            else:
                # Possible threat: anyone can update those values with a valid sale order name that is not hard to find.
                # update partner
                if country:
                    partner.country_id = country
                partner.write({
                    'name': '{} {}'.format(data['form_fields']['lastname'], data['form_fields']['firstname']),
                    'street': data['form_fields']['address'],
                    'city': data['form_fields']['city'],
                    'zip': data['form_fields']['zip'],
                    'phone': data['form_fields']['phone'],
                })
                # post survey on partner record
                if any([key in data['form_fields'] for key in ['mc_known', 'influence', 'find_out', 'household']]):
                    title = _('MC Care Website Survey')
                    q_1 = _('Did your know Marie\'s Corner before your purchase ?')
                    q_2 = _('Did the MC Care warranty influence your purchase ?')
                    q_3 = _('How did you find out about the MC Care Warranty ?')
                    q_4 = _('Household Type')
                    a_1 = data['form_fields']['mc_known'] if 'mc_known' in data['form_fields']['influence'] else _('No Response')
                    a_2 = data['form_fields']['influence'] if 'influence' in data['form_fields']['influence'] else _('No Response')
                    a_3 = data['form_fields']['find_out'] if 'find_out' in data['form_fields']['influence'] else _('No Response')
                    a_4 = data['form_fields']['household'] if 'household' in data['form_fields']['influence'] else _('No Response')
                    survey_msg = '<p><strong>{}</strong><br/>{} -> {}<br/>{} -> {}<br/>{} -> {}<br/>{} -> {}</p>'.format(title, q_1, a_1, q_2, a_2, q_3, a_3, q_4, a_4)
                    partner.message_post(body=survey_msg, subject=title, message_type='comment', subtype='mail.mt_note')
            # update sale order
            sale_order.write({'mc_care_warranty': True, 'final_partner_id': partner.id})
            # update sales lots
            sale_order.order_line.mapped('sales_lot_id').write({'mc_care_warranty': True, 'final_partner_id': partner.id})
            # If we encounter an issue while extracting data, abort registration
        except Exception as e:
            warranty_error = e.args[0]
            return request.render("mc_warranty.warranty_not_activated", {'error': warranty_error})
        # TODO send an email for confirmation!
        return request.render("mc_warranty.warranty_activated")

    def extract_data(self, values):
        """
        Extract data from request parameters
        If there are missing mandatory fields or if it is not possible to convert them in the right type
        raise an error
        """
        error_fields = []
        custom_fields = []
        data = {'form_fields': dict()}

        for field_name, field_value in values.items():
            if field_name in self.authorized_fields:
                try:
                    if self.authorized_fields[field_name]['type'] == 'phone':
                        data['form_fields'][field_name] = self.phone_format(field_name, field_value, country=values.get('country', None))
                    else:
                        input_filter = self._input_filters[self.authorized_fields[field_name]['type']]
                        response = input_filter(self, field_name, field_value)
                        if response:
                            data['form_fields'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)
                except KeyError:
                    error_fields.append(field_name)
            else:
                custom_fields.append((field_name, field_value))

        data['custom_fields'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        missing_required_fields = [label for label, field in self.authorized_fields.items() if field['required'] and not label in data['form_fields']]
        if error_fields or missing_required_fields:
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def date(self, field_label, field_input):
        return datetime.strptime(field_input, '%Y-%m-%d')

    def phone_format(self, field_label, field_input, country=None):
        if country and not isinstance(country, models.Model):
            try:
                country = request.env['res.country'].browse(int(country))
            except Exception:
                return ValueError(_('Could not convert phone number (wrong country id format: {})').format(country))
        return phone_validation.phone_format(
            field_input,
            country.code if country else None,
            country.phone_code if country else None,
            force_format='INTERNATIONAL',
            raise_exception=False
        )

    def selection(self, field_label, field_input):
        # TODO: should we handle different languages ?
        lang = request.env['ir.qweb.field'].user_lang()
        values = {
            '': False,
            'yes': 'Yes',
            'no': 'No',
            'not_know': 'I did not know',
            'knew_but_no': 'I knew, but no',
            'little': 'A little bit',
            'moderately': 'Moderately',
            'a_lot': 'A lot',
            'absolutely': 'Absolutely',
            'unpack': 'Unpacking the products',
            'leaflets': 'Leafleats and brochures',
            'press': 'By the press',
            'social': 'Via social networks',
            'store': 'Via a Store/Reseller',
            'designer': 'By my Architect/Designer',
            'website': 'Via the website of Marie\'s Corner',
            'trade': 'At a trade show',
            'event': 'During an event',
            'mouth': 'By word of mouth',
            'other': 'Other',
            'single': 'Single',
            'relationship': 'In a relationship',
            'family_child': 'Family (w/ child(ren) < 12 years old)',
            'family_teen': 'Family (w/ child(ren) > 12 years old)',
            'retired': 'Retired(s)'
        }
        return values[field_input]

    _input_filters = {
        'char': identity,
        'date': date,
        'selection': selection,
        'integer': integer,
        'phone': phone_format,
    }

    # TODO: why reseller and date are mandatory ? We do not use them
    authorized_fields = {
        'firstname': {'type': 'char', 'required': True},
        'lastname': {'type': 'char', 'required': True},
        'address': {'type': 'char', 'required': True},
        'city': {'type': 'char', 'required': True},
        'zip': {'type': 'char', 'required': True},
        'country': {'type': 'integer', 'required': True},
        'email': {'type': 'char', 'required': True},
        'phone': {'type': 'phone', 'required': True},
        'reseller': {'type': 'char', 'required': True},
        'date': {'type': 'date', 'required': True},
        'warranty': {'type': 'char', 'required': True},
        'mc_known': {'type': 'char', 'required': False},
        'influence': {'type': 'selection', 'required': False},
        'find_out': {'type': 'selection', 'required': False},
        'household': {'type': 'selection', 'required': False},
    }
