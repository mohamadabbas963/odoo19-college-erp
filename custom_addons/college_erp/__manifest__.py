{
    'name': 'College ERP',
    'version': '19.0.1.1',
    'license': 'LGPL-3',
    'author': 'Back End With Mohamad',
    'category': 'Education',
    'summary': 'An ERP for college education',
    'description': """
Form students administration to exams, covering all aspects of college administration.
    """,
    'website': 'https://www.back-end.com',
    'sequence': 1,
    'depends': [
        'base',
        'mail',  # لإضافة سجل النشاطات والمراسلات (Chatter)
        'product',  # لإدارة أنواع الرسوم كمنتجات خدمية
        'account',  # للنظام المالي والفواتير
    ],
    'data': [
        # 1. الحماية والصلاحيات (دائماً في البداية)
        "security/college_erp_security.xml",
        "security/ir.model.access.csv",

        # 2. البيانات الأساسية والتسلسلات
        "data/ir.sequence.csv",
        "views/college_department_views.xml",

        "views/college_course_views.xml",

        # 3. واجهات الموديلات المساعدة (Views Only)
        "views/college_attendance_views.xml",
        "views/college_fees_views.xml",
        "views/college_fee_type_views.xml",
        "views/college_certificate_views.xml",
        "views/college_appointment_views.xml",
        "views/account_move_views.xml",
        "views/college_erp_teacher_views.xml",

        "views/college_course_registration_views.xml",

        # 4. واجهات الطالب (Views) - تعريف الأشكال قبل استخدامها
        "views/college_student_views.xml",  # يحتوي على Search View
        "views/college_student_kanban.xml",  # يحتوي على Kanban View

        # 5. الأكشنز (Actions) - تعتمد على الواجهات أعلاه
        "views/college_student_actions.xml",

        # 6. الإضافات (Smart Buttons / Inherited Views)
        "views/college_student_smart_buttons.xml",

        # 7. القوائم (Menus) - تعتمد على الأكشنز
        "views/college_erp_menus.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
