from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CollegeAttendance(models.Model):
    _name = "college.attendance"
    _description = "College Attendance"

    # ===========================
    # BASIC FIELDS
    # ===========================
    student_id = fields.Many2one(
        'college.student',
        string="Student",
        required=True,
        ondelete='cascade'
    )
    check_in = fields.Datetime(
        string="Check In",
        required=True,
        default=fields.Datetime.now  # تعيين قيمة افتراضية للوقت الحالي
    )
    check_out = fields.Datetime(string="Check Out")
    duration = fields.Float(
        string="Duration (hours)",
        compute="_compute_duration",
        store=True
    )

    # ===========================
    # RELATED FIELDS FOR DISPLAY
    # ===========================
    student_name = fields.Char(
        string="Student Name",
        related='student_id.name',
        store=True,
        readonly=True
    )
    admission_no = fields.Char(
        string="Admission Number",
        related='student_id.admission_no',
        store=True,
        readonly=True
    )

    # ===========================
    # COMPUTE METHODS
    # ===========================
    @api.depends('check_in', 'check_out')
    def _compute_duration(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                delta = rec.check_out - rec.check_in
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0

    # ===========================
    # ACTION METHODS (NEW)
    # ===========================
    def action_check_out(self):
        """تُعيّن وقت الخروج وتُحسب المدة."""
        self.ensure_one()

        # نتحقق إذا كان حقل check_out فارغاً:
        if not self.check_out:
            # نُعين الوقت الحالي للحقل check_out:
            self.check_out = fields.Datetime.now()
            # Odoo سيقوم بتحديث حقل duration تلقائياً