# -*- coding: utf-8 -*-
from odoo import models, fields


class CollegeCertificate(models.Model):
    _name = "college.certificate"
    _description = "Student Certificate"

    student_id = fields.Many2one("college.student", string="Student")
    certificate_name = fields.Char(string="Certificate")
    issued_date = fields.Date(string="Issued Date")

    # Related fields للعرض
    student_name = fields.Char(related="student_id.name", store=True, readonly=True)
    admission_no = fields.Char(
        related="student_id.admission_no", store=True, readonly=True
    )
