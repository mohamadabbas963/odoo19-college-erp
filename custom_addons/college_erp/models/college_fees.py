# -*- coding: utf-8 -*-
from odoo import models, fields, api


# ==============================================================
# 1. نموذج نوع الرسوم (Master Data)
# ==============================================================
class CollegeFeeType(models.Model):
    _name = "college.fee.type"
    _description = "College Fee Type"
    name = fields.Char(string="Fee Type Name", required=True)


# ==============================================================
# 2. نموذج سجل الرسوم (Fees Record)
# ==============================================================
class CollegeFees(models.Model):
    _name = "college.fees"
    _description = "Student Fees"

    # --- الحقول ---
    name = fields.Char(
        string="Reference", required=True, copy=False, readonly=True, default="New"
    )
    fee_date = fields.Date(
        string="Fee Date", default=fields.Date.today
    )  # ⬅️ حقل مفقود تم إضافته
    student_id = fields.Many2one("college.student", string="Student", required=True)
    student_name = fields.Char(related="student_id.name", store=True, readonly=True)
    admission_no = fields.Char(
        related="student_id.admission_no", store=True, readonly=True
    )
    fee_amount = fields.Float(string="Fee Amount")

    # ✅ استخدام حقل Many2one الديناميكي (بدلاً من Selection)
    fee_type_id = fields.Many2one("college.fee.type", string="Fee Type", required=True)

    state = fields.Selection([("paid", "Paid"), ("unpaid", "Unpaid")], default="unpaid")


    # --- دالة التسلسل ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("college.fees") or "New"
                )
        return super(CollegeFees, self).create(vals_list)
