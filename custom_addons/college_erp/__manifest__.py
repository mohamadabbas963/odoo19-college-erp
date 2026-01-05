{
    "name": "College ERP",
    "version": "19.0.1.0.0",
    "author": "Mohamad Abbas, Odoo Community Association (OCA)",
    "category": "Education",
    "summary": "Comprehensive ERP solution for University Management",
    "website": "https://github.com/mohamadabbas963/odoo19-college-erp",
    "sequence": 1,
    "depends": [
        "base",
        "mail",  # لإضافة سجل النشاطات والمراسلات (Chatter)
        "product",  # لإدارة أنواع الرسوم كمنتجات خدمية
        "account",  # للنظام المالي والفواتير
    ],
    "data": [
        # 1. الحماية والصلاحيات (دائماً في البداية)
        "security/college_erp_security.xml",
        "security/ir.model.access.csv",
        # 2. البيانات الأساسية والتسلسلات
        "data/ir.sequence.csv",
        "views/college_department_views.xml",
        "views/college_course_views.xml",
        # 3. واجهات الموديلات المساعدة (Views Only)
        "views/college_attendance_views.xml",
        "views/college_exam_result_views.xml",
        "views/college_fees_views.xml",
        "views/college_fee_type_views.xml",
        "views/college_certificate_views.xml",
        "views/college_appointment_views.xml",
        "views/account_move_views.xml",
        "views/college_classroom_view.xml",
        "views/college_erp_teacher_views.xml",
        "views/college_course_registration_views.xml",
        # 4. واجهات الطالب (Views) - تعريف الأشكال قبل استخدامها
        "views/college_student_views.xml",  # يحتوي على Search View
        "views/college_student_kanban.xml",  # يحتوي على Kanban View
        # 5. الأكشنز (Actions) - تعتمد على الواجهات أعلاه
        "views/college_student_actions.xml",
        # 6. الإضافات (Smart Buttons / Inherited Views)
        "views/college_student_smart_buttons.xml",
        "reports/college_exam_report.xml",
        "reports/college_payment_report.xml",
        # 7. القوائم (Menus) - تعتمد على الأكشنز
        "views/college_erp_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "college_erp/static/src/xml/student_dashboard.xml",
            "college_erp/static/src/js/student_dashboard.js",
        ],
    },
    "application": True,
    "license": "LGPL-3",
}
