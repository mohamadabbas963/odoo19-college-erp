from odoo import models, fields, api

class CollegeTeacher(models.Model):
    _name = "college.teacher"
    _description = "College Teacher"
    _rec_name = "name"
    _order = "name"

    # ---------- BASIC FIELDS ----------
    name = fields.Char(string="Full Name", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone Number")
    hire_date = fields.Date(string="Hire Date")
    active = fields.Boolean(string="Active", default=True)

    # ---------- RELATION FIELDS ----------
    department_id = fields.Many2one('college.department', string="Department")
    student_ids = fields.Many2many('college.student', string="Students")

    # ---------- COMPUTED FIELDS ----------
    student_count = fields.Integer(
        string="Number of Students",
        compute="_compute_student_count"
    )

    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
