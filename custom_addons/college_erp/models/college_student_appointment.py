# -*- coding: utf-8 -*-
""" University Management System """
# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class CollegeAppointment(models.Model):
    _name = "college.student.appointment"
    _description = "Academic Appointments"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "appointment_datetime desc"

    # حقل الترقيم التلقائي
    name = fields.Char(string="Reference", readonly=True, copy=False, default="New")
    student_id = fields.Many2one(
        "college.student", string="Student", required=True, tracking=True
    )

    # حقول معلومات إضافية للقراءة فقط
    admission_no = fields.Char(
        related="student_id.admission_no", string="Admission No", readonly=True
    )
    department_id = fields.Many2one(
        related="student_id.department_id", string="Department", readonly=True
    )

    appointment_datetime = fields.Datetime(
        string="Date & Time", default=fields.Datetime.now, tracking=True
    )
    purpose = fields.Selection(
        [
            ("academic", "Academic Advising"),
            ("financial", "Financial Matters"),
            ("registration", "Registration"),
        ],
        string="Purpose",
        required=True,
        default="academic",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Completed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    notes = fields.Text(string="Notes")

    # وظيفة الترقيم التلقائي
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("college.student.appointment")
                    or "New"
                )
        return super().create(vals_list)

    def action_confirm(self):
        self.state = "confirmed"

    def action_done(self):
        self.state = "done"

    def action_create_invoice(self):
        for rec in self:
            # التحقق من وجود طالب مرتبط
            if not rec.student_id:
                continue

            # إنشاء مسودة فاتورة (Draft Invoice)
            invoice_vals = {
                "move_type": "out_invoice",
                "partner_id": rec.student_id.partner_id.id,
                "student_id": rec.student_id.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Academic Appointment Fee: {rec.name}",
                            "quantity": 1,
                            "price_unit": 50.0,
                        },
                    )
                ],
            }
            new_invoice = self.env["account.move"].create(invoice_vals)

            # تحديث حالة الموعد (اختياري)
            rec.state = "done"

            # العودة لفتح الفاتورة الجديدة أمام المستخدم
            return {
                "name": "Appointment Invoice",
                "view_mode": "form",
                "res_model": "account.move",
                "res_id": new_invoice.id,
                "type": "ir.actions.act_window",
            }
