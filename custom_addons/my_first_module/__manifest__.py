{
    'name': 'My First Module',
    'version': '1.0',
    'category': 'Custom',
    'summary': 'A professional starter module for Odoo development',
    'author': 'Mohamad',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_model_views.xml',
    ],
    'installable': True,
    'application': True,
}
