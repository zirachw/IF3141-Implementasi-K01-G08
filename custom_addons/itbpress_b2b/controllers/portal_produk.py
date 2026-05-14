from odoo import http
from odoo.http import request

from .internal_helpers import STAGE_STYLE, _no_cache, _require_portal


class PortalProduk(http.Controller):

    @http.route('/kolaborasi/produk-saya', type='http', auth='public', website=True)
    def produk_saya(self, stage_filter=None, search='', **kw):
        redir = _require_portal()
        if redir:
            return redir
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id), ('type', '=', 'opportunity')]
        if stage_filter:
            domain.append(('stage_id.name', '=', stage_filter))
        if search:
            domain.append(('name', 'ilike', search))

        leads = request.env['crm.lead'].sudo().search(domain, order='date_open desc')
        flash = request.session.pop('flash_success', None)
        return _no_cache(request.render('itbpress_b2b.portal_produk_saya', {
            'active_menu': 'produk_saya',
            'leads': leads,
            'stage_style': STAGE_STYLE,
            'stage_filter': stage_filter or '',
            'search': search,
            'flash_success': flash,
        }))

    @http.route('/kolaborasi/produk-saya/<int:lead_id>', type='http', auth='public', website=True)
    def produk_detail(self, lead_id, **kw):
        redir = _require_portal()
        if redir:
            return redir
        partner = request.env.user.partner_id
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.partner_id.id != partner.id:
            return request.not_found()

        return _no_cache(request.render('itbpress_b2b.portal_produk_detail', {
            'active_menu': 'produk_saya',
            'lead': lead,
            'stage_style': STAGE_STYLE,
            'hpp_records': lead.x_hpp_ids.sudo().sorted('tanggal_entri'),
        }))
