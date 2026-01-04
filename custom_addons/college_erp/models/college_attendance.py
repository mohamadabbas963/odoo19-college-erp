from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CollegeAttendance(models.Model):
    _name = "college.attendance"
    _description = "College Academic Attendance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # --- 1. الحقول الأساسية (Basic Fields) ---
    name = fields.Char(string="Reference", readonly=True, default="/")
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Completed')
    ], string="Status", default='draft', tracking=True)

    # --- 2. حقول الربط (Relational Fields) ---
    course_id = fields.Many2one('college.course', string="Course", required=True)
    teacher_id = fields.Many2one('college.teacher', string="Teacher", required=True)
    classroom_id = fields.Many2one('college.classroom', string="Classroom")
    attendance_line_ids = fields.One2many(
        'college.attendance.line',
        'attendance_id',
        string="Students Attendance"
    )

    # --- 3. دوال الـ ORM (ORM Methods) ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('college.attendance') or '/'
        return super().create(vals_list)

    # --- 4. دوال التحقق (Constraints) ---
    @api.constrains('course_id', 'teacher_id', 'date')
    def _check_unique_attendance(self):
        for rec in self:
            domain = [
                ('course_id', '=', rec.course_id.id),
                ('teacher_id', '=', rec.teacher_id.id),
                ('date', '=', rec.date),
                ('id', '!=', rec.id),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(_("Attendance for this course and teacher has already been recorded for today!"))

    # --- 5. دوال الأزرار والأكشنز (Action Methods) ---

    def action_load_students(self):
        """سحب الطلاب بناءً على المادة (Course Registration)"""
        self.ensure_one()
        if self.state == 'done':
            raise ValidationError(_("You cannot reload students for a completed attendance record."))

        self.attendance_line_ids = [(5, 0, 0)]
        confirmed_registrations = self.env['college.course.registration.line'].search([
            ('course_id', '=', self.course_id.id),
            ('registration_id.state', '=', 'confirmed')
        ])

        if not confirmed_registrations:
            raise ValidationError(_("No confirmed students found for this course!"))

        attendance_lines = []
        for reg in confirmed_registrations:
            attendance_lines.append((0, 0, {
                'student_id': reg.registration_id.student_id.id,
                'status': 'present',
            }))
        self.attendance_line_ids = attendance_lines

    def action_generate_attendance_list(self):
        """سحب الطلاب بناءً على القاعة (Smart Classroom)"""
        for rec in self:
            if not rec.classroom_id:
                raise ValidationError(_("Please select a classroom first!"))

            if rec.state == 'done':
                raise ValidationError(_("You cannot change attendance for a completed record."))

            rec.attendance_line_ids = [(5, 0, 0)]
            lines = []
            for student in rec.classroom_id.assigned_student_ids:
                lines.append((0, 0, {
                    'student_id': student.id,
                    'status': 'present',
                }))
            rec.attendance_line_ids = lines

    def action_confirm(self):
        self.state = 'done'

    def action_set_to_draft(self):
        self.state = 'draft'


class CollegeAttendanceLine(models.Model):
    _name = "college.attendance.line"
    _description = "Attendance Line"

    attendance_id = fields.Many2one('college.attendance', ondelete='cascade')
    student_id = fields.Many2one('college.student', string="Student", readonly=True)
    admission_no = fields.Char(related='student_id.admission_no', string="Admission No")

    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused')
    ], string="Status", default='present')

    remark = fields.Char(string="Notes")