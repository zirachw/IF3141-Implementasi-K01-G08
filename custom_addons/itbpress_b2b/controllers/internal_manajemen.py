import json
from datetime import datetime

from odoo import http
from odoo.http import request

from .internal_helpers import (
    STAGE_STYLE, STAGE_XMLID, SALURAN_LABEL, JENIS_LABEL, SISTEM_LABEL,
    _no_cache, _is_marketing, _is_internal, _require_internal, _user_role,
)


class ManajemenController(http.Controller):

    @http.route('/manajemen', type='http', auth='public', website=True)
    def manajemen(self, search='', stage_filter='', **kw):
        redir = _require_internal()
        if redir:
            return redir

        domain = [('x_tipe_produksi', '!=', False), ('type', '=', 'opportunity')]
        if stage_filter:
            domain.append(('stage_id.name', '=', stage_filter))
        if search:
            domain += ['|', ('name', 'ilike', search), ('partner_id.name', 'ilike', search)]

        leads = request.env['crm.lead'].sudo().search(domain, order='date_open desc')
        return _no_cache(request.render('itbpress_b2b.internal_manajemen', {
            'active_menu': 'manajemen',
            'leads': leads,
            'stage_style': STAGE_STYLE,
            'stage_filter': stage_filter,
            'search': search,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
            'flash_success': request.session.pop('flash_success', None),
        }))

    @http.route('/manajemen/<int:lead_id>', type='http', auth='public', website=True)
    def manajemen_detail(self, lead_id, **kw):
        redir = _require_internal()
        if redir:
            return redir

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or not lead.x_tipe_produksi:
            return request.not_found()

        hpp_records = lead.x_hpp_ids.sudo().sorted('tanggal_entri', reverse=True)
        penjualan_records = lead.x_penjualan_ids.sudo().sorted('tanggal', reverse=True)

        return _no_cache(request.render('itbpress_b2b.internal_manajemen_detail', {
            'active_menu': 'manajemen',
            'lead': lead,
            'stage_style': STAGE_STYLE,
            'hpp_records': hpp_records,
            'penjualan_records': penjualan_records,
            'saluran_label': SALURAN_LABEL,
            'jenis_label': JENIS_LABEL,
            'sistem_label': SISTEM_LABEL,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
            'flash_success': request.session.pop('flash_success', None),
        }))

    @http.route('/manajemen/<int:lead_id>/ubah-stage', type='http', auth='public', website=True, methods=['POST'])
    def manajemen_ubah_stage(self, lead_id, **post):
        if not _is_marketing():
            return request.redirect('/manajemen/%d' % lead_id)

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.not_found()

        stage_name = post.get('stage_name', '')
        xmlid = STAGE_XMLID.get(stage_name)
        stage = request.env.ref(xmlid, raise_if_not_found=False) if xmlid else None
        if stage:
            vals = {'stage_id': stage.id}
            if stage_name == 'Dalam Produksi':
                try:
                    vals['x_harga_lisensi_confirmed'] = float(post.get('harga_lisensi', 0))
                except ValueError:
                    pass
            lead.sudo().write(vals)
            request.session['flash_success'] = 'Stage diubah ke %s.' % stage_name

        return request.redirect('/manajemen/%d' % lead_id)

    @http.route('/manajemen/<int:lead_id>/edit', type='http', auth='public', website=True, methods=['POST'])
    def manajemen_edit(self, lead_id, **post):
        if not _is_marketing():
            return request.redirect('/manajemen/%d' % lead_id)

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.not_found()

        vals = {}
        for key, field in [
            ('nama_produk', 'name'), ('nama_pic', 'x_nama_pic'),
            ('kontak_pic', 'x_kontak_pic'), ('tipe_produksi', 'x_tipe_produksi'),
            ('jenis_produk', 'x_jenis_produk'), ('sistem', 'x_sistem'),
            ('catatan', 'description'),
        ]:
            if post.get(key):
                vals[field] = post[key]
        if post.get('kuantitas_produksi'):
            try:
                vals['x_kuantitas_produksi'] = int(post['kuantitas_produksi'])
            except ValueError:
                pass
        if post.get('rencana_harga_lisensi'):
            try:
                vals['x_rencana_harga_lisensi'] = float(post['rencana_harga_lisensi'])
            except ValueError:
                pass

        if vals:
            lead.sudo().write(vals)
        request.session['flash_success'] = 'Pengajuan berhasil diperbarui.'
        return request.redirect('/manajemen/%d' % lead_id)

    # ------------------------------------------------------------------ #
    #  JSON chart endpoints                                              #
    # ------------------------------------------------------------------ #

    @http.route('/manajemen/chart/tren', type='http', auth='public')
    def chart_tren(self, lead_id=None, partner_id=None, date_from=None, date_to=None, **kw):
        if not _is_internal():
            return request.make_response(json.dumps([]), headers=[('Content-Type', 'application/json')])

        domain = []
        if lead_id:
            domain.append(('pengajuan_id', '=', int(lead_id)))
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
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
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/manajemen/chart/saluran', type='http', auth='public')
    def chart_saluran(self, lead_id=None, partner_id=None, date_from=None, date_to=None, **kw):
        if not _is_internal():
            return request.make_response(json.dumps([]), headers=[('Content-Type', 'application/json')])

        domain = []
        if lead_id:
            domain.append(('pengajuan_id', '=', int(lead_id)))
        if partner_id:
            domain.append(('partner_id', '=', int(partner_id)))
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
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/manajemen/chart/hpp/<int:lead_id>', type='http', auth='public')
    def chart_hpp(self, lead_id, **kw):
        if not _is_internal():
            return request.make_response(json.dumps([]), headers=[('Content-Type', 'application/json')])

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.make_response(json.dumps([]), headers=[('Content-Type', 'application/json')])

        data = [{'tanggal': str(h.tanggal_entri), 'hpp': h.total_hpp}
                for h in lead.x_hpp_ids.sudo().sorted('tanggal_entri')]
        return request.make_response(json.dumps(data), headers=[('Content-Type', 'application/json')])
