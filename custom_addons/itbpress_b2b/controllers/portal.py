from odoo import http
from odoo.addons.portal.controllers.web import Home as PortalHome
from odoo.addons.web.controllers.utils import is_user_internal
from odoo.http import request

def _is_itbpress_internal(uid):
    user = request.env['res.users'].sudo().browse(uid)
    return user.has_group('itbpress_b2b.group_staf_marketing') \
        or user.has_group('itbpress_b2b.group_direktur')


class Home(PortalHome):

    def _login_redirect(self, uid, redirect=None):
        if not redirect:
            if not is_user_internal(uid):
                redirect = '/kolaborasi'
            elif _is_itbpress_internal(uid):
                redirect = '/manajemen'
        return super()._login_redirect(uid, redirect=redirect)

    @http.route()
    def index(self, *args, **kw):
        if request.session.uid:
            if not is_user_internal(request.session.uid):
                return request.redirect_query('/kolaborasi', query=request.params)
            if _is_itbpress_internal(request.session.uid):
                return request.redirect_query('/manajemen', query=request.params)
        return request.redirect('/web/login')

    @http.route()
    def web_client(self, s_action=None, **kw):
        if request.session.uid:
            if not is_user_internal(request.session.uid):
                return request.redirect_query('/kolaborasi', query=request.params)
            if _is_itbpress_internal(request.session.uid):
                return request.redirect_query('/manajemen', query=request.params)
        return super().web_client(s_action, **kw)
