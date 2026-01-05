# -*- coding: utf-8 -*-
""" University Management System """
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CollegeExamResult(models.Model):
    _name = "college.exam.result"
    _description = "Student Exam Result"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "exam_date desc"

    name = fields.Char(string="Reference", readonly=True, default="/")
    student_id = fields.Many2one(
        "college.student", string="Student", required=True, tracking=True
    )
    department_id = fields.Many2one(
        related="student_id.department_id", store=True, string="Department"
    )
    exam_date = fields.Date(
        string="Exam Date", default=fields.Date.context_today, required=True
    )

    result_line_ids = fields.One2many(
        "college.exam.result.line", "result_id", string="Exam Scores"
    )

    total_marks = fields.Float(
        string="Total Marks", compute="_compute_final_result", store=True
    )
    average_percentage = fields.Float(
        string="Percentage", compute="_compute_final_result", store=True
    )
    status = fields.Selection(
        [("pass", "Passed"), ("fail", "Failed")],
        string="Final Status",
        compute="_compute_final_result",
        store=True,
    )

    @api.depends("result_line_ids.score")
    def _compute_final_result(self):
        for rec in self:
            scores = rec.result_line_ids.mapped("score")
            count = len(scores)
            rec.total_marks = sum(scores)
            rec.average_percentage = (
                (rec.total_marks / (count * 100)) * 100 if count > 0 else 0
            )
            # الطالب ينجح إذا كان معدله فوق 50% ولم يرسب في أي مادة (اختياري)
            rec.status = "pass" if rec.average_percentage >= 50 else "fail"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("college.exam.result") or "/"
                )
        return super().create(vals_list)

    # --- الدالة الذكية (أضفها هنا) ---
    def action_load_courses(self):
        """سحب المواد التي سجلها الطالب في موديول التسجيل وأكدها"""
        self.ensure_one()
        if not self.student_id:
            raise ValidationError(self.env._("الرجاء اختيار الطالب أولاً!"))

        # 1. البحث عن التسجيلات المؤكدة للطالب
        registrations = self.env["college.course.registration.line"].search(
            [
                ("registration_id.student_id", "=", self.student_id.id),
                ("registration_id.state", "=", "confirmed"),
            ]
        )

        if not registrations:
            raise ValidationError(self.env._("لا يوجد مواد مسجلة ومؤكدة لهذا الطالب."))

        # 2. تجهيز الأسطر (مسح القديم وإضافة الجديد)
        lines = []
        for reg in registrations:
            lines.append(
                (
                    0,
                    0,
                    {
                        "course_id": reg.course_id.id,
                        "max_score": 100.0,
                        "score": 0.0,
                    },
                )
            )

        self.write({"result_line_ids": [(5, 0, 0)] + lines})


class CollegeExamResultLine(models.Model):
    _name = "college.exam.result.line"
    _description = "Exam Result Line"

    result_id = fields.Many2one("college.exam.result", ondelete="cascade")
    course_id = fields.Many2one("college.course", string="Course", required=True)
    max_score = fields.Float(string="Max Score", default=100.0)
    score = fields.Float(string="Obtained Score")
    grade = fields.Char(string="Grade", compute="_compute_grade", store=True)

    @api.depends("score")
    def _compute_grade(self):
        for line in self:
            if line.score >= 90:
                line.grade = "A+"
            elif line.score >= 80:
                line.grade = "A"
            elif line.score >= 70:
                line.grade = "B"
            elif line.score >= 60:
                line.grade = "C"
            elif line.score >= 50:
                line.grade = "D"
            else:
                line.grade = "F"
