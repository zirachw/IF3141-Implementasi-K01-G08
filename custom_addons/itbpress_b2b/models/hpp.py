from odoo import api, fields, models


class Hpp(models.Model):
    _name = 'x.hpp'
    _description = 'Histori HPP'
    _order = 'tanggal_entri desc, id desc'

    pengajuan_id = fields.Many2one(
        'crm.lead', string='Pengajuan',
        required=True, ondelete='cascade',
    )
    partner_id = fields.Many2one(
        related='pengajuan_id.partner_id',
        store=True, string='Mitra',
    )
    total_hpp = fields.Float(string='HPP per Unit (Rp)', required=True, digits=(15, 2))
    tanggal_entri = fields.Date(string='Tanggal', required=True)
    stempel_waktu = fields.Datetime(string='Stempel Waktu', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        now = fields.Datetime.now()
        for vals in vals_list:
            vals.setdefault('stempel_waktu', now)
        return super().create(vals_list)
