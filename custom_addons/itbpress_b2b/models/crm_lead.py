from odoo import api, fields, models

from ..constants import JENIS_PRODUK, SISTEM, TIPE_PRODUKSI


class CrmLeadB2B(models.Model):
    _inherit = 'crm.lead'

    x_nama_pic = fields.Char(string='Nama PIC')
    x_kontak_pic = fields.Char(string='Kontak PIC')
    x_tipe_produksi = fields.Selection(TIPE_PRODUKSI, string='Tipe Produksi')
    x_jenis_produk = fields.Selection(JENIS_PRODUK, string='Jenis Produk')
    x_sistem = fields.Selection(SISTEM, string='Sistem')
    x_kuantitas_produksi = fields.Integer(string='Kuantitas Produksi (pcs)')
    x_rencana_harga_lisensi = fields.Float(string='Rencana Harga Lisensi (Rp/unit)', digits=(15, 2))
    x_harga_lisensi_confirmed = fields.Float(string='Harga Lisensi (Rp/unit)', digits=(15, 2))

    x_tab_penjualan_aktif = fields.Boolean(
        string='Tab Penjualan Aktif',
        compute='_compute_tab_penjualan_aktif',
        store=True,
    )

    x_penjualan_ids = fields.One2many(
        'x.data.penjualan', 'pengajuan_id',
        string='Data Penjualan',
    )
    x_hpp_ids = fields.One2many(
        'x.hpp', 'pengajuan_id',
        string='Histori HPP',
    )

    @api.depends('stage_id.is_won')
    def _compute_tab_penjualan_aktif(self):
        for lead in self:
            lead.x_tab_penjualan_aktif = lead.stage_id.is_won

    @api.model
    def _cleanup_builtin_demo(self):
        self.search([('x_tipe_produksi', '=', False)]).unlink()

    def action_buka_wizard_dalam_produksi(self):
        self.ensure_one()
        wizard = self.env['itbpress.wizard.dalam.produksi'].create({
            'lead_id': self.id,
            'harga_lisensi': self.x_rencana_harga_lisensi,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Konfirmasi Harga Lisensi: Dalam Produksi',
            'res_model': 'itbpress.wizard.dalam.produksi',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
