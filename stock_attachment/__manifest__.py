{
    'name': 'Stock Picking Attachments',
    'version': '17.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Додає можливість прикріплення файлів до надходжень товарів',
    'description': """
Stock Picking Attachments
========================
Цей модуль додає можливість завантаження файлів до складських операцій.

Основні можливості:
------------------
* Завантаження файлів до надходжень товарів
* Підтримка різних форматів файлів
* Зручний інтерфейс завантаження
* Інтеграція з існуючими складськими операціями
    """,
    'author': 'GabSoft',
    'website': 'https://yourwebsite.com',
    'depends': [
        'base',
        'stock',
        'sale',
        'board'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'data/check_low_stock.xml',

        'views/receiving_wood.xml',
        'views/stock_picking_views.xml',
        'views/res_partner_view.xml',
        'views/recycling_rates_grade_pivot.xml',
        'views/churak_production_report.xml',
        'views/res_config_settings.xml',

        'views/ir_attachment_view.xml',

        'views/operations_view.xml',
        'views/stock_dashboard.xml',
        'views/stock_menu.xml',
        'views/mrp_menue.xml',
    ],

    'images': ['static/description/icon.svg'],
    'installable': True,

    'assets': {
        'web.assets_backend': [
            'stock_attachment/static/src/components/**/*.js',
            'stock_attachment/static/src/components/**/*.xml',
            'stock_attachment/static/src/components/**/*.scss',

            'stock_attachment/static/src/js/*.js',
            'stock_attachment/static/src/xml/*.xml',
            'stock_attachment/static/src/css/*.css'
        ],
    },

    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}