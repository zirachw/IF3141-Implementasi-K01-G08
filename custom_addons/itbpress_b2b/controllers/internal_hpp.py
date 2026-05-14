from odoo import http
from odoo.http import request

from .internal_helpers import _no_cache, _is_marketing, _require_internal, _user_role


class HppController(http.Controller):

    @http.route('/hpp', type='http', auth='public', website=True)
    def hpp(self, search='', **kw):
        redir = _require_internal()
        if redir:
            return redir

        domain = [('x_tipe_produksi', '=', 'itb_press'), ('type', '=', 'opportunity')]
        if search:
            domain += ['|', ('name', 'ilike', search), ('partner_id.name', 'ilike', search)]

        leads = request.env['crm.lead'].sudo().search(domain, order='partner_id, date_open desc')

        hpp_summary = []
        for lead in leads:
            latest = lead.x_hpp_ids.sudo().sorted('tanggal_entri', reverse=True)
            hpp_summary.append({
                'lead': lead,
                'hpp_terkini': latest[0].total_hpp if latest else 0,
                'terakhir_diperbarui': latest[0].tanggal_entri if latest else None,
            })

        return _no_cache(request.render('itbpress_b2b.internal_hpp', {
            'active_menu': 'hpp',
            'hpp_summary': hpp_summary,
            'search': search,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
        }))

    @http.route('/hpp/<int:lead_id>', type='http', auth='public', website=True)
    def hpp_detail(self, lead_id, **kw):
        redir = _require_internal()
        if redir:
            return redir

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists() or lead.x_tipe_produksi != 'itb_press':
            return request.not_found()

        hpp_records = lead.x_hpp_ids.sudo().sorted('tanggal_entri', reverse=True)

        return _no_cache(request.render('itbpress_b2b.internal_hpp_detail', {
            'active_menu': 'hpp',
            'lead': lead,
            'hpp_records': hpp_records,
            'is_marketing': _is_marketing(),
            'user_role': _user_role(),
            'flash_success': request.session.pop('flash_success', None),
            'flash_error': request.session.pop('flash_error', None),
        }))

    @http.route('/hpp/<int:lead_id>/tambah', type='http', auth='public', website=True, methods=['POST'])
    def hpp_tambah(self, lead_id, **post):
        if not _is_marketing():
            return request.redirect('/hpp/%d' % lead_id)

        lead = request.env['crm.lead'].sudo().browse(lead_id)
        if not lead.exists():
            return request.not_found()

        try:
            request.env['x.hpp'].sudo().create({
                'pengajuan_id': lead_id,
                'total_hpp': float(post['total_hpp']),
                'tanggal_entri': post['tanggal_entri'],
            })
            request.session['flash_success'] = 'Entri HPP berhasil ditambahkan.'
        except Exception:
            request.session['flash_error'] = 'Gagal menyimpan entri HPP. Periksa kembali data yang dimasukkan.'

        return request.redirect('/hpp/%d' % lead_id)
