from odoo import fields, models

from ..constants import SALURAN


class Penjualan(models.Model):
    _name = 'x.data.penjualan'
    _description = 'Data Penjualan Per Saluran Distribusi'
    _order = 'tanggal desc'

    pengajuan_id = fields.Many2one(
        'crm.lead', string='Pengajuan',
        required=True, ondelete='cascade',
    )
    partner_id = fields.Many2one(
        related='pengajuan_id.partner_id',
        store=True, string='Mitra',
    )
    saluran = fields.Selection(SALURAN, string='Saluran Distribusi', required=True)
    tanggal = fields.Date(string='Tanggal', required=True)
    jumlah_terjual = fields.Integer(string='Jumlah Terjual (pcs)', required=True)
    nilai_penjualan = fields.Float(string='Nilai Penjualan (Rp)', required=True, digits=(15, 2))
