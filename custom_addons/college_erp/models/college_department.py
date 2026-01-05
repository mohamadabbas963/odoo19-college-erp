# -*- coding: utf-8 -*-
from odoo import models, fields, api


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
    student_ids = fields.One2many("college.student", "department_id", string="Students")
    students_count = fields.Integer(
        string="Number of Students", compute="_compute_students_count"
    )

    @api.depends("student_ids")
    def _compute_students_count(self):
        for rec in self:
            # حساب عدد الطلاب المرتبطين بالقسم
            rec.students_count = len(rec.student_ids)

    def action_view_department_students(self):
        """
        يفتح عرضاً (Action) يحتوي على قائمة بجميع الطلاب
        المرتبطين بالقسم الحالي.
        """
        # نضمن أن هذا الإجراء يتم على سجل واحد فقط
        self.ensure_one()

        # بناء الإجراء (Action) الذي سيتم تنفيذه
        return {
            "name": "Students in " + self.name,
            "view_mode": "list,form",
            "res_model": "college.student",
            "type": "ir.actions.act_window",
            "domain": [("department_id", "=", self.id)],
            "context": {
                "default_department_id": self.id
            },  # عند إنشاء طالب جديد، يتم تعيين القسم تلقائيًا
        }
