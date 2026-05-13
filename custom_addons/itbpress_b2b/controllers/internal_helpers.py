from datetime import date, datetime

from odoo.http import request

from ..constants import JENIS_PRODUK, SISTEM, SALURAN

STAGE_STYLE = {
    'Diajukan':       'background:#f3f4f6;color:#6b7280',
    'Negosiasi':      'background:#eff6ff;color:#075BA9',
    'Dalam Produksi': 'background:#fffbeb;color:#d97706',
    'Dirilis':        'background:#f0fdf4;color:#16a34a',
    'Ditolak':        'background:#fef2f2;color:#dc2626',
}

STAGE_XMLID = {
    'Diajukan':       'itbpress_b2b.status_diajukan',
    'Negosiasi':      'itbpress_b2b.status_negosiasi',
    'Dalam Produksi': 'itbpress_b2b.status_dalam_produksi',
    'Dirilis':        'itbpress_b2b.status_dirilis',
    'Ditolak':        'itbpress_b2b.status_ditolak',
}

JENIS_LABEL   = dict(JENIS_PRODUK)
SISTEM_LABEL  = dict(SISTEM)
SALURAN_LABEL = dict(SALURAN)


def _no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    return response


def _is_marketing():
    return request.env.user.has_group('itbpress_b2b.group_staf_marketing')


def _is_internal():
    return (request.env.user.has_group('itbpress_b2b.group_staf_marketing') or
            request.env.user.has_group('itbpress_b2b.group_direktur'))


def _require_portal():
    if not request.session.uid:
        return request.redirect('/web/login')
    if _is_internal():
        return request.redirect('/manajemen')
    return None


def _require_internal():
    if not request.session.uid:
        return request.redirect('/web/login')
    if _is_internal():
        return None
    if request.env.user.has_group('base.group_portal'):
        return request.redirect('/kolaborasi/produk-saya')
    return request.redirect('/web/login')


def _parse_date(s, fallback):
    if not s:
        return fallback
    try:
        return datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError:
        return fallback


def _date_range_defaults(entries_asc):
    if entries_asc:
        return entries_asc[0].tanggal, entries_asc[-1].tanggal
    today = date.today()
    return date(today.year, today.month, 1), today


def _user_role():
    if _is_marketing():
        return 'Staf Marketing'
    return 'Direktur'
