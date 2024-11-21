{
    'name': 'Raw Materials Receipt Report',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Звіт про прийом сировини',
    'sequence': 100,
    'author': 'GabSoft',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['stock', 'base_setup'],
    'data': [
        'data/paperformat.xml',
        'security/ir.model.access.csv',
        'views/stock_menu.xml',
        'reports/raw_materials_report.xml',
        'wizards/raw_materials_report_wizard_views.xml',
    ],
    'external_dependencies': {
        'python': ['dateutil']
    },
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}