from odoo import fields, models


class WizardDalamProduksi(models.TransientModel):
    _name = 'itbpress.wizard.dalam.produksi'
    _description = 'Konfirmasi Harga Lisensi: Pindah ke Dalam Produksi'

    lead_id = fields.Many2one('crm.lead', string='Pengajuan', required=True)
    harga_lisensi = fields.Float(
        string='Harga Lisensi (Rp/unit)',
        digits=(15, 2),
        required=True,
    )

    def action_konfirmasi(self):
        stage = self.env.ref('itbpress_b2b.status_dalam_produksi', raise_if_not_found=False)
        self.lead_id.write({
            'stage_id': stage.id if stage else self.lead_id.stage_id.id,
            'x_harga_lisensi_confirmed': self.harga_lisensi,
        })
        return {'type': 'ir.actions.act_window_close'}
