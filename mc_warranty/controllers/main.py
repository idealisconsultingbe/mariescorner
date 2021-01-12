# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError

from odoo import models, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.addons.phone_validation.tools import phone_validation



class RegisterProductsForm(http.Controller):

    @http.route('/register_products/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def register_products(self, model_name, **kwargs):
        try:
            data = self.extract_data(request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

    def extract_data(self, values):
        error_fields = []
        custom_fields = []
        data = {'record': dict()}

        for field_name, field_value in values.items():
            if field_name in self.authorized_fields:
                try:
                    if self.authorized_fields[field_name]['type'] == 'phone':
                        data['record'][field_name] = self.phone_format(field_name, field_value, country=values.get('country', None))
                    else:
                        input_filter = self._input_filters[self.authorized_fields[field_name]['type']]
                        data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)
            else:
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        missing_required_fields = [label for label, field in self.authorized_fields.items() if field['required'] and not label in data['record']]
        if error_fields or missing_required_fields:
            raise ValidationError(error_fields + missing_required_fields)

        return data

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def boolean(self, field_label, field_input):
        return bool(int(field_input))

    def date(self, field_label, field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        return datetime.strptime(field_input, lang.date_format).strftime(DEFAULT_SERVER_DATE_FORMAT)

    def phone_format(self, field_label, field_input, country=None):
        if country and not isinstance(country, models.Model):
            try:
                country = request.env['res.country'].browse(int(country))
            except Exception:
                return ValueError(_('Could not convert phone number (wrong country id: {})').format(country))
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
        'many2one': integer,
        'selection': selection,
        'boolean': boolean,
        'integer': integer,
        'phone': phone_format,
        'email': identity,
    }

    authorized_fields = {
        'firstname': {'type': 'char', 'required': True},
        'lastname': {'type': 'char', 'required': True},
        'address': {'type': 'char', 'required': True},
        'city': {'type': 'char', 'required': True},
        'zip': {'type': 'char', 'required': True},
        'country': {'type': 'integer', 'required': True},
        'email': {'type': 'email', 'required': True},
        'phone': {'type': 'phone', 'required': True},
        'reseller': {'type': 'char', 'required': True},
        'date': {'type': 'date', 'required': True},
        'warranty': {'type': 'char', 'required': True},
        'mc_known': {'type': 'boolean', 'required': False},
        'influence': {'type': 'selection', 'required': False},
        'find_out': {'type': 'selection', 'required': False},
        'household': {'type': 'selection', 'required': False},
    }