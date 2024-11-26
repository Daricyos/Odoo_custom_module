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
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',

        'views/receiving_wood.xml',
        'views/stock_picking_views.xml',

        'views/ir_attachment_view.xml',
    ],

    'images': ['static/description/icon.svg'],
    'installable': True,

    'assets': {
        'web.assets_backend': [
            # 'stock_attachment/static/src/js/kanban_button.js',
            # 'stock_attachment/static/src/xml/inventory_kanban_button.xml'
            'stock_attachment/static/src/**/*',
        ],
    },

    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}