import json
from datetime import datetime

from odoo import http
from odoo.http import request

from .internal_helpers import SALURAN_LABEL, _no_cache, _parse_date, _date_range_defaults, _require_portal


class PortalPenjualan(http.Controller):

    @http.route('/kolaborasi/penjualan', type='http', auth='public', website=True)
    def penjualan(self, date_from=None, date_to=None, **kw):
        redir = _require_portal()
        if redir:
            return redir
        partner = request.env.user.partner_id
        dirilis_leads = request.env['crm.lead'].sudo().search([
            ('partner_id', '=', partner.id),
            ('x_tab_penjualan_aktif', '=', True),
        ], order='date_open desc')

        has_any_leads = bool(request.env['crm.lead'].sudo().search([
            ('partner_id', '=', partner.id),
            ('type', '=', 'opportunity'),
        ], limit=1))

        df_str = dt_str = ''
        product_stats = []

        if dirilis_leads:
            all_entries = request.env['x.data.penjualan'].sudo().search(
                [('partner_id', '=', partner.id)],
                order='tanggal asc',
            )
            default_from, default_to = _date_range_defaults(all_entries)
            df = _parse_date(date_from, default_from)
            dt = _parse_date(date_to, default_to)
            df_str = df.strftime('%Y-%m-%d')
            dt_str = dt.strftime('%Y-%m-%d')

            for lead in dirilis_leads:
                entries = request.env['x.data.penjualan'].sudo().search([
                    ('pengajuan_id', '=', lead.id),
                    ('tanggal', '>=', df),
                    ('tanggal', '<=', dt),
                ])
                product_stats.append({
                    'lead': lead,
                    'total_terjual': sum(e.jumlah_terjual for e in entries),
                    'total_nilai': sum(e.nilai_penjualan for e in entries),
                })

        return _no_cache(request.render('itbpress_b2b.portal_penjualan', {
            'active_menu': 'penjualan',
            'has_dirilis': bool(dirilis_leads),
            'has_any_leads': has_any_leads,
            'product_stats': product_stats,
            'date_from': df_str,
            'date_to': dt_str,
        }))

    @http.route('/kolaborasi/penjualan/<int:lead_id>', type='http', auth='public', website=True)
    def penjualan_detail(self, lead_id, date_from=None, date_to=None, **kw):
        redir = _require_portal()
        if redir:
            return redir
        partner = request.env.user.partner_id
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.partner_id.id != partner.id or not lead.x_tab_penjualan_aktif:
            return request.not_found()

        all_entries = request.env['x.data.penjualan'].sudo().search(
            [('pengajuan_id', '=', lead_id)],
            order='tanggal asc',
        )
        default_from, default_to = _date_range_defaults(all_entries)
        df = _parse_date(date_from, default_from)
        dt = _parse_date(date_to, default_to)
        df_str = df.strftime('%Y-%m-%d')
        dt_str = dt.strftime('%Y-%m-%d')

        entries = request.env['x.data.penjualan'].sudo().search([
            ('pengajuan_id', '=', lead_id),
            ('tanggal', '>=', df),
            ('tanggal', '<=', dt),
        ], order='tanggal desc')

        return _no_cache(request.render('itbpress_b2b.portal_penjualan_detail', {
            'active_menu': 'penjualan',
            'lead': lead,
            'entries': entries,
            'saluran_label': SALURAN_LABEL,
            'date_from': df_str,
            'date_to': dt_str,
        }))

    @http.route('/kolaborasi/chart/tren', type='http', auth='public')
    def chart_tren(self, lead_id=None, date_from=None, date_to=None, **kw):
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        if lead_id:
            domain.append(('pengajuan_id', '=', int(lead_id)))
        if date_from:
            try:
                domain.append(('tanggal', '>=', datetime.strptime(date_from, '%Y-%m-%d').date()))
            except ValueError:
                pass
        if date_to:
            try:
                domain.append(('tanggal', '<=', datetime.strptime(date_to, '%Y-%m-%d').date()))
            except ValueError:
                pass

        entries = request.env['x.data.penjualan'].sudo().search(domain)
        monthly = {}
        for e in entries:
            key = e.tanggal.strftime('%Y-%m') if e.tanggal else 'Unknown'
            monthly[key] = monthly.get(key, 0) + e.nilai_penjualan

        data = [{'bulan': k, 'total': monthly[k]} for k in sorted(monthly.keys())]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )

    @http.route('/kolaborasi/chart/saluran', type='http', auth='public')
    def chart_saluran(self, lead_id=None, date_from=None, date_to=None, **kw):
        partner = request.env.user.partner_id
        domain = [('partner_id', '=', partner.id)]
        if lead_id:
            domain.append(('pengajuan_id', '=', int(lead_id)))
        if date_from:
            try:
                domain.append(('tanggal', '>=', datetime.strptime(date_from, '%Y-%m-%d').date()))
            except ValueError:
                pass
        if date_to:
            try:
                domain.append(('tanggal', '<=', datetime.strptime(date_to, '%Y-%m-%d').date()))
            except ValueError:
                pass

        entries = request.env['x.data.penjualan'].sudo().search(domain)
        per_saluran = {}
        for e in entries:
            label = SALURAN_LABEL.get(e.saluran, e.saluran)
            per_saluran[label] = per_saluran.get(label, 0) + e.nilai_penjualan

        data = [{'saluran': k, 'total': v} for k, v in per_saluran.items()]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )

    @http.route('/kolaborasi/chart/hpp/<int:lead_id>', type='http', auth='public')
    def chart_hpp(self, lead_id, **kw):
        partner = request.env.user.partner_id
        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.partner_id.id != partner.id:
            return request.make_response(
                json.dumps([]),
                headers=[('Content-Type', 'application/json')],
            )

        data = [{
            'tanggal': str(h.tanggal_entri),
            'hpp': h.total_hpp,
        } for h in lead.x_hpp_ids.sudo().sorted('tanggal_entri')]
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
        )
