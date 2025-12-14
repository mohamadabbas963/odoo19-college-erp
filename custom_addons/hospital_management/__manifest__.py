{
    'name': 'Hospital Management System',
    'author': 'Wlnut Software Solutions',
    'license': 'LGPL-3',
    'version': '19.0.1.0',
    'depends': ['base', 'mail', 'product', 'account',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/patient_views.xml',  # ضع sequence بعد تعريف الحقول
        'views/patient_readonly_views.xml',
        'views/appointment_views.xml',
        'views/appointment_line_views.xml',
        'views/patient_tag_views.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'images': ['static/description/icon.png'],
}