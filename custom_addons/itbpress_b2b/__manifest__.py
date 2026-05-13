{
    'name': 'ITB Press: B2B Customer Portal',
    'version': '17.0.1.0.0',
    'category': 'CRM',
    'summary': 'Sistem manajemen kolaborasi produk B2B untuk ITB Press',
    'depends': ['crm', 'website'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/crm_stage_data.xml',
        'views/wizard_dalam_produksi.xml',
        'views/crm_lead_views.xml',
        'views/penjualan_views.xml',
        'views/hpp_views.xml',
        'views/menu.xml',
        'views/login_template.xml',
        'views/portal_base.xml',
        'views/portal_pengajuan.xml',
        'views/portal_produk.xml',
        'views/portal_penjualan.xml',
        'views/internal_base.xml',
        'views/internal_manajemen.xml',
        'views/internal_laporan.xml',
        'views/internal_hpp.xml',
    ],
    'demo': [
        'data/demo_users.xml',
        'data/demo_leads.xml',
        'data/demo_cleanup.xml',
    ],
    'assets': {
        # Website pages (login, portal) — loaded by web.frontend_layout
        'web.assets_frontend': [
            'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap',
            'itbpress_b2b/static/src/css/login.css',
        ],
        # Custom bundle for internal pages (/manajemen, /laporan, /hpp)
        # Loaded explicitly via t-call-assets in internal_base.xml
        'itbpress_b2b.assets_internal': [
            'itbpress_b2b/static/src/css/internal.css',
        ],
        # Custom bundle for portal pages (/kolaborasi/*)
        # Loaded explicitly via t-call-assets in portal_base.xml
        'itbpress_b2b.assets_portal': [
            'itbpress_b2b/static/src/css/portal.css',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
}
