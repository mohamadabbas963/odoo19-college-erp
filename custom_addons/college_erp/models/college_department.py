from odoo import models, fields

class CollegeDepartment(models.Model):
    _name = "college.department"
    _description = "College Department"
    _rec_name = "name"
    _order = "name"

    # ---------- BASIC FIELDS ----------
    name = fields.Char(string="Department Name", required=True)
    code = fields.Char(string="Department Code")
    description = fields.Text(string="Description")

    # ---------- RELATION FIELDS ----------
    student_ids = fields.One2many(
        'college.student',
        'department_id',
        string="Students"
    )
