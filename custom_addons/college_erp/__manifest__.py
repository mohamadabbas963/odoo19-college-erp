{
    'name': 'College ERP',
    'version': '19.0.1.1',
    'license': 'LGPL-3',
    'author': 'Back End With Mohamad',
    'category': 'Education',
    'summary': 'An ERP for college education',
    'description': 'Form students administration to exams, covering all aspects of college administration.',
    'website': 'https://www.back-end.com',
    'sequence': 1,
    'data': [
        # ---------------------
        # Security
        # ---------------------
        "security/college_erp_security.xml",
        "security/ir.model.access.csv",

        # ---------------------
        # Views for linked models first
        # ---------------------
        "views/college_attendance_views.xml",
        "views/college_fees_views.xml",
        "views/college_fees_sequence.xml",
        "views/college_fee_type_views.xml",
        "views/college_certificate_views.xml",

        # ---------------------
        # Main student view after actions exist
        # ---------------------
        "views/college_student_views.xml",
        "views/college_student_kanban.xml",
        "views/college_student_actions.xml",
        "views/college_student_smart_buttons.xml",
        "views/college_department_views.xml",

        # ---------------------
        # Menus
        # ---------------------
        "views/college_erp_menus.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
