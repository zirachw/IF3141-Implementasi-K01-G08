from odoo import http
from odoo.http import request

from .internal_helpers import (
    SALURAN_LABEL,
    _no_cache, _is_marketing, _require_internal, _parse_date, _date_range_defaults, _user_role,
)


class LaporanController(http.Controller):

    @http.route('/laporan', type='http', auth='public', website=True)
    def laporan(self, date_from=None, date_to=None, **kw):
        redir = _require_internal()
        if redir:
            return redir

        dirilis_leads = request.env['crm.lead'].sudo().search([
            ('x_tab_penjualan_aktif', '=', True),
            ('x_tipe_produksi', '!=', False),
        ])

        all_entries = request.env['x.data.penjualan'].sudo().search([], order='tanggal asc')
        default_from, default_to = _date_range_defaults(all_entries)
        df = _parse_date(date_from, default_from)
        dt = _parse_date(date_to, default_to)
        df_str = df.strftime('%Y-%m-%d')
        dt_str = dt.strftime('%Y-%m-%d')

        partners_map = {}
        for lead in dirilis_leads:
            if not lead.partner_id:
                continue
            pid = lead.partner_id.id
            if pid not in partners_map:
                partners_map[pid] = {'partner': lead.partner_id, 'leads': []}
            partners_map[pid]['leads'].append(lead)

        partner_stats = []
        for pid, pdata in partners_map.items():
            total_terjual = total_nilai = 0
            for lead in pdata['leads']:
                entries = request.env['x.data.penjualan'].sudo().search([
                    ('pengajuan_id', '=', lead.id),
                    ('tanggal', '>=', df), ('tanggal', '<=', dt),
                ])
                total_terjual += sum(e.jumlah_terjual for e in entries)
                total_nilai += sum(e.nilai_penjualan for e in entries)
            partner_stats.append({
                'partner': pdata['partner'],
                'total_terjual': total_terjual,
                'total_nilai': total_nilai,
                'produk_count': len(pdata['leads']),
            })

        return _no_cache(request.render('itbpress_b2b.internal_laporan', {
            'active_menu': 'laporan',
            'partner_stats': partner_stats,
            'date_from': df_str,
            'date_to': dt_str,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
        }))

    @http.route('/laporan/<int:partner_id>', type='http', auth='public', website=True)
    def laporan_mitra(self, partner_id, date_from=None, date_to=None, **kw):
        redir = _require_internal()
        if redir:
            return redir

        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            return request.not_found()

        dirilis_leads = request.env['crm.lead'].sudo().search([
            ('partner_id', '=', partner_id),
            ('x_tab_penjualan_aktif', '=', True),
        ], order='date_open desc')

        all_entries = request.env['x.data.penjualan'].sudo().search(
            [('partner_id', '=', partner_id)], order='tanggal asc')
        default_from, default_to = _date_range_defaults(all_entries)
        df = _parse_date(date_from, default_from)
        dt = _parse_date(date_to, default_to)
        df_str = df.strftime('%Y-%m-%d')
        dt_str = dt.strftime('%Y-%m-%d')

        product_stats = []
        for lead in dirilis_leads:
            entries = request.env['x.data.penjualan'].sudo().search([
                ('pengajuan_id', '=', lead.id),
                ('tanggal', '>=', df), ('tanggal', '<=', dt),
            ])
            product_stats.append({
                'lead': lead,
                'total_terjual': sum(e.jumlah_terjual for e in entries),
                'total_nilai': sum(e.nilai_penjualan for e in entries),
            })

        return _no_cache(request.render('itbpress_b2b.internal_laporan_mitra', {
            'active_menu': 'laporan',
            'partner': partner,
            'product_stats': product_stats,
            'date_from': df_str,
            'date_to': dt_str,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
        }))

    @http.route('/laporan/<int:partner_id>/<int:lead_id>', type='http', auth='public', website=True)
    def laporan_produk(self, partner_id, lead_id, date_from=None, date_to=None, **kw):
        redir = _require_internal()
        if redir:
            return redir

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.partner_id.id != partner_id:
            return request.not_found()

        all_entries = request.env['x.data.penjualan'].sudo().search(
            [('pengajuan_id', '=', lead_id)], order='tanggal asc')
        default_from, default_to = _date_range_defaults(all_entries)
        df = _parse_date(date_from, default_from)
        dt = _parse_date(date_to, default_to)
        df_str = df.strftime('%Y-%m-%d')
        dt_str = dt.strftime('%Y-%m-%d')

        entries = request.env['x.data.penjualan'].sudo().search([
            ('pengajuan_id', '=', lead_id),
            ('tanggal', '>=', df), ('tanggal', '<=', dt),
        ], order='tanggal desc')

        return _no_cache(request.render('itbpress_b2b.internal_laporan_produk', {
            'active_menu': 'laporan',
            'lead': lead,
            'entries': entries,
            'saluran_label': SALURAN_LABEL,
            'date_from': df_str,
            'date_to': dt_str,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
            'flash_success': request.session.pop('flash_success', None),
            'flash_error': request.session.pop('flash_error', None),
        }))

    @http.route('/laporan/<int:partner_id>/<int:lead_id>/tambah',
                type='http', auth='public', website=True, methods=['POST'])
    def laporan_tambah_entri(self, partner_id, lead_id, **post):
        if not _is_marketing():
            return request.redirect('/laporan/%d/%d' % (partner_id, lead_id))

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.partner_id.id != partner_id:
            return request.not_found()

        try:
            request.env['x.data.penjualan'].sudo().create({
                'pengajuan_id': lead_id,
                'saluran': post['saluran'],
                'tanggal': post['tanggal'],
                'jumlah_terjual': int(post['jumlah_terjual']),
                'nilai_penjualan': float(post['nilai_penjualan']),
            })
            request.session['flash_success'] = 'Entri penjualan berhasil ditambahkan.'
        except Exception:
            request.session['flash_error'] = 'Gagal menyimpan entri penjualan. Periksa kembali data yang dimasukkan.'

        return request.redirect('/laporan/%d/%d' % (partner_id, lead_id))

    @http.route('/laporan/<int:partner_id>/<int:lead_id>/hapus/<int:entry_id>',
                type='http', auth='public', website=True, methods=['POST'])
    def laporan_hapus_entri(self, partner_id, lead_id, entry_id, **post):
        if not _is_marketing():
            return request.redirect('/laporan/%d/%d' % (partner_id, lead_id))

        entry = request.env['x.data.penjualan'].sudo().browse(entry_id)
        if entry.exists() and entry.pengajuan_id.id == lead_id:
            entry.sudo().unlink()
            request.session['flash_success'] = 'Entri berhasil dihapus.'

        return request.redirect('/laporan/%d/%d' % (partner_id, lead_id))
