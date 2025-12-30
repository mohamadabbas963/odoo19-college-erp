from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # ربط الفاتورة بالطالب (موجود لديك)
    student_id = fields.Many2one(
        'college.student',
        string="Student",
        help="The student associated with this invoice"
    )

    # إضافة هذا السطر لحل مشكلة رسالة الخطأ
    # هذا سيربط الحقل الموجود في الواجهة بموديل المواعيد الخاص بالكلية
    appointment_id = fields.Many2one(
        'college.student.appointment',
        string="Appointment"
    )