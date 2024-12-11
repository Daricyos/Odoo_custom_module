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

        'views/receiving_wood.xml',
        'views/stock_picking_views.xml',

        'views/ir_attachment_view.xml',

        'views/operations_view.xml',
        'views/stock_menu.xml',
    ],

    'images': ['static/description/icon.svg'],
    'installable': True,

    'assets': {
        'web.assets_backend': [
            'stock_attachment/static/src/js/kpi_card.js',
            'stock_attachment/static/src/js/camera.js',
            'stock_attachment/static/src/js/beech_aggregate_dashboard.js',
            'stock_attachment/static/src/xml/dashboard.xml',
            'stock_attachment/static/src/xml/kpi_card.xml',
            'stock_attachment/static/src/xml/camera.xml',
            'stock_attachment/static/src/css/styles.css'
            # 'stock_attachment/static/src/js/kanban_button.js',
            # 'stock_attachment/static/src/xml/inventory_kanban_button.xml'
            # 'stock_attachment/static/src/**/*',
        ],
    },

    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}