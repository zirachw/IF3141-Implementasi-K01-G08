from odoo import http
from odoo.http import request

from .internal_helpers import _no_cache, _require_portal


class PortalIndex(http.Controller):

    @http.route('/kolaborasi', type='http', auth='public', website=True)
    def index(self, **kw):
        redir = _require_portal()
        if redir:
            return redir
        return request.redirect('/kolaborasi/produk-saya')


class PortalPengajuan(http.Controller):

    @http.route('/kolaborasi/baru', type='http', auth='public', website=True)
    def pengajuan_form(self, **kw):
        redir = _require_portal()
        if redir:
            return redir
        return _no_cache(request.render('itbpress_b2b.portal_pengajuan', {
            'active_menu': 'pengajuan',
            'error': kw.get('error'),
            'csrf_token': request.csrf_token(),
        }))

    @http.route('/kolaborasi/submit', type='http', auth='public', website=True, methods=['POST'])
    def submit_pengajuan(self, **post):
        redir = _require_portal()
        if redir:
            return redir
        required = ['nama_produk', 'nama_pic', 'kontak_pic', 'tipe_produksi',
                    'jenis_produk', 'sistem', 'kuantitas_produksi', 'rencana_harga_lisensi']
        if not all(post.get(f) for f in required):
            return request.redirect('/kolaborasi/baru?error=required')

        partner = request.env.user.partner_id
        stage = request.env.ref('itbpress_b2b.status_diajukan', raise_if_not_found=False)
        request.env['crm.lead'].sudo().create({
            'name': post['nama_produk'],
            'partner_id': partner.id,
            'type': 'opportunity',
            'stage_id': stage.id if stage else False,
            'x_nama_pic': post['nama_pic'],
            'x_kontak_pic': post['kontak_pic'],
            'x_tipe_produksi': post['tipe_produksi'],
            'x_jenis_produk': post['jenis_produk'],
            'x_sistem': post['sistem'],
            'x_kuantitas_produksi': int(post.get('kuantitas_produksi', 0)),
            'x_rencana_harga_lisensi': float(post.get('rencana_harga_lisensi', 0)),
            'description': post.get('catatan', ''),
        })
        request.session['flash_success'] = 'Pengajuan berhasil dikirim.'
        return request.redirect('/kolaborasi/produk-saya')
