# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.osv.expression import OR


class CustomerPortal(CustomerPortal):

    MANDATORY_FIELDS = ["external_state"]
    OPTIONAL_FIELDS = ["ext_delivery_date", "shipped_date", "manufacturing_date"]

    def _prepare_portal_layout_values(self):
        """
        Overridden method
        Compute sales lot count for portal home
        """
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        sales_lot_count = request.env['stock.production.sales.lot'].search_count([('partner_ids', '=', partner.id)])

        values.update({
            'sales_lot_count': sales_lot_count,
        })
        return values

    @http.route(['/my/manufacturing_numbers', '/my/manufacturing_numbers/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_sales_lots(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='number', **kw):
        """ Route handling list view of manufacturing numbers related to user """
        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Manufacturing Number'), 'order': 'name desc'},
            'state': {'label': _('Manufacturing State'), 'order': 'external_state'},
            'sale_order': {'label': _('Sale Order'), 'order': 'origin_sale_order_id'},
            'partner': {'label': _('Customer'), 'order': 'partner_id'},
            'manufacturing_date': {'label': _('Manufacturing Date'), 'order': 'manufacturing_date desc'},
            'shipped_date': {'label': _('Shipped Date'), 'order': 'shipped_date desc'},
        }

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [('partner_ids', '=', partner.id)]},
        }

        searchbar_inputs = {
            'message': {'input': 'message', 'label': _('Search in Messages')},
            # 'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'state': {'input': 'state', 'label': _('Search in States')},
            # 'sale_order': {'input': 'sale_order', 'label': _('Search in Sales Order')},
            'number': {'input': 'number', 'label': _('Search Numbers')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }

        # default sortby order
        if not sortby:
            sortby = 'name'
        sort_order = searchbar_sortings[sortby]['order']

        # default filter by all
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # in case we could archive manufacturing numbers
        archive_groups = self._get_archive_groups('stock.production.sales.lot', domain)

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('number', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            # if search_in in ('customer', 'all'):
            #     search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            if search_in in ('state', 'all'):
                search_domain = OR([search_domain, [('external_state', 'ilike', search)]])
            # if search_in in ('sale_order', 'all'):
            #     search_domain = OR([search_domain, [('origin_sale_order_id', 'ilike', search)]])
            domain += search_domain

        # count for pager
        Sales_lot = request.env['stock.production.sales.lot']
        sales_lot_count = Sales_lot.search_count(domain)

        # make pager
        pager = portal_pager(
            url="/my/manufacturing_numbers",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'filterby': filterby, 'search_in': search_in, 'search': search},
            total=sales_lot_count,
            page=page,
            step=self._items_per_page
        )

        # search the count to display, according to the pager data
        sales_lots = Sales_lot.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_manufacturing_numbers_history'] = sales_lots.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'sales_lots': sales_lots.sudo(),
            'page_name': 'manufacturing_numbers',
            'archive_groups': archive_groups,
            'default_url': '/my/manufacturing_numbers',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("mc_sales_lot.my_sales_lots_portal", values)

    @http.route(['/my/manufacturing_number/<int:sales_lot_id>'], type='http', auth="public", website=True)
    def portal_my_sales_lot(self, sales_lot_id, access_token=None, **kw):
        """ Route handling view of specific manufacturing numbers related to user """
        # check access of user according to security rules
        try:
            sales_lot_sudo = self._document_check_access('stock.production.sales.lot', sales_lot_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # redirect to /my if user is not a subcontractor
        partner = request.env.user.partner_id
        if sales_lot_sudo and partner not in sales_lot_sudo.partner_ids:
            return request.redirect('/my')

        values = self._sales_lot_get_page_view_values(sales_lot_sudo, access_token, **kw)
        return request.render("mc_sales_lot.my_sales_lot_portal", values)

    @http.route(['/my/manufacturing_number/edit/<int:sales_lot_id>'], type='http', auth='user', website=True)
    def edit_sale_lot(self, sales_lot_id, access_token=None, redirect=None, **post):
        """ Route handling edit view of specific manufacturing numbers related to user """
        # check access of user according to security rules
        try:
            sales_lot_sudo = self._document_check_access('stock.production.sales.lot', sales_lot_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # redirect to /my if user is not a subcontractor
        partner = request.env.user.partner_id
        if sales_lot_sudo and partner not in sales_lot_sudo.partner_ids:
            return request.redirect('/my')

        values = self._sales_lot_get_page_view_values(sales_lot_sudo, access_token, **post)
        values.update({
            'error': {},
            'error_message': [],
        })

        # form validation and generation of error messages
        if post and request.httprequest.method == 'POST':
            error, error_message = self.sales_lot_form_validate(sales_lot_sudo, post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_FIELDS if key in post})
                sales_lot_sudo.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/manufacturing_numbers')

        values['redirect'] = redirect
        response = request.render("mc_sales_lot.edit_sales_lot_portal", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def sales_lot_form_validate(self, sales_lot, data):
        """
        Validate form values
        Check for mandatory fields, dates logic, unknown fields and return error messages
        """
        error = dict()
        error_message = []

        # mandatory fields validation
        for field_name in self.MANDATORY_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # dates validation: ext_delivery_date >= shipped_date >= manufacturing_date
        shipped_date = data.get('shipped_date', sales_lot.shipped_date)
        manufacturing_date = data.get('manufacturing_date', sales_lot.manufacturing_date)
        delivery_date = data.get('ext_delivery_date', sales_lot.ext_delivery_date)

        if shipped_date and manufacturing_date and shipped_date < manufacturing_date:
            if data.get('shipped_date') or data.get('manufacturing_date'):
                error_message.append(_('Shipped date should not be earlier than manufacturing date.'))
                if data.get('shipped_date'):
                    error['shipped_date'] = 'error'
                if data.get('manufacturing_date'):
                    error['manufacturing_date'] = 'error'
        elif shipped_date and delivery_date and shipped_date < delivery_date:
            if data.get('shipped_date') or data.get('ext_delivery_date'):
                error_message.append(_('Delivery date should not be later than shipped date.'))
                if data.get('shipped_date'):
                    error['shipped_date'] = 'error'
                if data.get('ext_delivery_date'):
                    error['ext_delivery_date'] = 'error'
        elif delivery_date and manufacturing_date and delivery_date < manufacturing_date:
            if data.get('ext_delivery_date') or data.get('manufacturing_date'):
                error_message.append(_('Delivery date should not be earlier than manufacturing date.'))
                if data.get('ext_delivery_date'):
                    error['ext_delivery_date'] = 'error'
                if data.get('manufacturing_date'):
                    error['manufacturing_date'] = 'error'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        # handling unknown fields
        unknown = [k for k in data if k not in self.MANDATORY_FIELDS + self.OPTIONAL_FIELDS]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append(_("Unknown field(s) '{}'").format(','.join(unknown)))

        return error, error_message

    def _sales_lot_get_page_view_values(self, sales_lot, access_token, **kwargs):
        """
        Return manufacturing number values used for template generation
        """
        values = {
            'page_name': 'manufacturing_number',
            'sales_lot': sales_lot,
            'user': request.env.user
        }
        return self._get_page_view_values(sales_lot, access_token, values, 'my_manufacturing_numbers_history', False, **kwargs)
