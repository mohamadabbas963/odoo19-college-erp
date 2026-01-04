from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CollegeClassroom(models.Model):
    _name = 'college.classroom'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # توسيع الموديل السابق
    _description = 'Smart Classroom'
    name = fields.Char(string="Room Name", required=True)

    capacity = fields.Integer(string="Capacity", required=True, default=30)
    # --- ربط الاختصاصات المسموح بها لهذه القاعة ---
    allowed_department_ids = fields.Many2many(
        'college.department',
        string="Allowed Specializations",
        help="حدد الاختصاصات التي يمكنها استخدام هذه القاعة"
    )

    # --- ربط الطلاب المسكنين حالياً في هذه القاعة ---
    # ملاحظة: هذا الربط يفيد في توزيع قاعات الامتحانات أو السكن أو حلقات البحث
    assigned_student_ids = fields.One2many(
        'college.student',
        'current_classroom_id',
        string="Assigned Students"
    )

    current_student_count = fields.Integer(
        string="Current Students",
        compute="_compute_student_count",
        store=True
    )

    available_seats = fields.Integer(
        string="Available Seats",
        compute="_compute_available_seats"
    )

    @api.depends('assigned_student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.current_student_count = len(rec.assigned_student_ids)

    @api.depends('capacity', 'current_student_count')
    def _compute_available_seats(self):
        for rec in self:
            rec.available_seats = rec.capacity - rec.current_student_count

    # --- خوارزمية التوزيع الذكي (Automated Distribution) ---
    def action_auto_distribute_students(self):
        """
        وظيفة ذكية: تبحث عن الطلاب الذين ينتمون للاختصاصات المسموحة
        وتوزعهم في القاعة حتى تمتلئ السعة.
        """
        for rec in self:
            if not rec.allowed_department_ids:
                raise ValidationError(_("يرجى تحديد الاختصاصات المسموحة أولاً!"))

            # البحث عن طلاب من نفس الاختصاص ليس لديهم قاعة حالياً
            students_to_assign = self.env['college.student'].search([
                ('department_id', 'in', rec.allowed_department_ids.ids),
                ('current_classroom_id', '=', False)
            ], limit=rec.available_seats)

            for student in students_to_assign:
                student.current_classroom_id = rec.id

    def action_clear_classroom(self):
        """فك ارتباط جميع الطلاب المسجلين في هذه القاعة"""
        for rec in self:
            # نقوم بتفريغ حقل القاعة لدى جميع الطلاب المرتبطين
            rec.assigned_student_ids.write({'current_classroom_id': False})
        return True