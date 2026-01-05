# -*- coding: utf-8 -*-
"""
University Management System - Student Model
This module handles student lifecycle, financial integration, and academics.
"""

from datetime import date
from odoo import fields, models, api
from odoo.exceptions import UserError


class CollegeStudent(models.Model):
    """Model representing a student in the university ERP system."""

    _name = "college.student"
    _description = "College Student"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {"res.partner": "partner_id"}

    # 1. Core Fields & Partner Link
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        ondelete="cascade",
        help="Link to the partner record of the student.",
    )
    current_classroom_id = fields.Many2one(
        "college.classroom",
        string="Allocated Classroom",
        help="The classroom where the student is currently assigned.",
    )

    image_128 = fields.Image(related="partner_id.image_128", readonly=False)
    image_1920 = fields.Image(related="partner_id.image_1920", readonly=False)

    admission_no = fields.Char(
        required=True, tracking=True, default="New"
    )
    first_name = fields.Char(required=True, tracking=True)
    last_name = fields.Char(required=True, tracking=True)

    # 2. Communication & Personal Info
    student_email = fields.Char(tracking=True)
    student_phone = fields.Char()
    student_mobile = fields.Char()
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")],
        required=True,
        tracking=True,
    )
    admission_date = fields.Date(
        required=True, default=fields.Date.context_today
    )
    date_of_birth = fields.Date(required=True)
    age = fields.Integer(compute="_compute_age", store=True)
    father_name = fields.Char()
    mother_name = fields.Char()
    communication_address = fields.Text()

    # 3. Department & Status
    department_id = fields.Many2one(
        "college.department", string="Department", tracking=True
    )
    status = fields.Selection(
        [
            ("new", "New"),
            ("active", "Active"),
            ("graduated", "Graduated"),
            ("blocked", "Blocked"),
        ],
        default="new",
        tracking=True,
    )

    # 4. Financials (Computed from Partner)
    currency_id = fields.Many2one(related="partner_id.currency_id")
    student_total_invoiced = fields.Monetary(
        compute="_compute_financials", store=True
    )
    student_credit = fields.Monetary(
        compute="_compute_financials", store=True
    )

    # 5. One2many Relations
    attendance_ids = fields.One2many(
        "college.attendance.line", "student_id", string="Attendance"
    )
    fees_ids = fields.One2many("college.fees", "student_id", string="Fees")
    certificate_ids = fields.One2many(
        "college.certificate", "student_id", string="Certificates"
    )

    # 6. Counters for Smart Buttons
    attendance_count = fields.Integer(compute="_compute_counts")
    fees_count = fields.Integer(compute="_compute_counts")
    certificate_count = fields.Integer(compute="_compute_counts")
    appointment_count = fields.Integer(compute="_compute_counts")
    registration_count = fields.Integer(compute="_compute_counts")
    exam_result_count = fields.Integer(compute="_compute_counts")

    _sql_constraints = [
        (
            "admission_no_unique",
            "UNIQUE (admission_no)",
            "Admission Number must be unique.",
        )
    ]

    @api.depends("partner_id.total_invoiced", "partner_id.credit")
    def _compute_financials(self):
        """Update financial data from the linked partner record."""
        for rec in self:
            rec.student_total_invoiced = rec.partner_id.total_invoiced
            rec.student_credit = rec.partner_id.credit

    @api.depends("date_of_birth")
    def _compute_age(self):
        """Calculate age based on date of birth."""
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.age = (
                    today.year
                    - rec.date_of_birth.year
                    - (
                        (today.month, today.day)
                        < (rec.date_of_birth.month, rec.date_of_birth.day)
                    )
                )
            else:
                rec.age = 0

    def _compute_counts(self):
        """Unified compute for all smart button counters."""
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)
            rec.fees_count = len(rec.fees_ids)
            rec.certificate_count = len(rec.certificate_ids)
            rec.appointment_count = self.env[
                "college.student.appointment"
            ].search_count([("student_id", "=", rec.id)])
            rec.registration_count = self.env[
                "college.course.registration"
            ].search_count([("student_id", "=", rec.id)])
            rec.exam_result_count = self.env["college.exam.result"].search_count(
                [("student_id", "=", rec.id)]
            )

    @api.onchange("first_name", "last_name")
    def _onchange_student_name(self):
        """Dynamic update of the student full name."""
        self.name = f"{self.first_name or ''} {self.last_name or ''}".strip()

    def action_activate(self):
        """Change status to Active."""
        self.write({"status": "active"})

    def action_graduate(self):
        """Logic to graduate a student after checking exam results."""
        for rec in self:
            last_result = self.env["college.exam.result"].search(
                [("student_id", "=", rec.id)], order="exam_date desc", limit=1
            )
            if not last_result:
                raise UserError(self.env._("Student must have an exam record to graduate."))
            if last_result.status != "pass":
                raise UserError(self.env._("Student cannot graduate with a failing status."))
            rec.write({"status": "graduated"})

    def action_block(self):
        """Change status to Blocked."""
        self.write({"status": "blocked"})

    def action_view_appointments(self):
        """Smart button action to view student appointments."""
        return {
            "name": self.env._("Academic Appointments"),
            "type": "ir.actions.act_window",
            "res_model": "college.student.appointment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }

    def action_view_exam_results(self):
        """Smart button action to view exam results."""
        self.ensure_one()
        return {
            "name": self.env._("Exam Results"),
            "type": "ir.actions.act_window",
            "res_model": "college.exam.result",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }

    def action_view_student_invoices(self):
        """Smart button action to view student invoices."""
        self.ensure_one()
        return {
            "name": self.env._("Student Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id), ("move_type", "=", "out_invoice")],
            "context": {
                "default_move_type": "out_invoice",
                "default_student_id": self.id,
                "default_partner_id": self.partner_id.id,
            },
        }

    def action_create_invoice(self):
        """Create an invoice from confirmed course registrations."""
        self.ensure_one()
        uninvoiced_registrations = self.env["college.course.registration"].search(
            [
                ("student_id", "=", self.id),
                ("state", "=", "confirmed"),
                ("is_invoiced", "=", False),
            ]
        )

        if not uninvoiced_registrations:
            return {
                "name": self.env._("Student Invoices"),
                "view_mode": "list,form",
                "res_model": "account.move",
                "type": "ir.actions.act_window",
                "domain": [
                    ("partner_id", "=", self.partner_id.id),
                    ("move_type", "=", "out_invoice"),
                ],
                "context": {"default_move_type": "out_invoice"},
            }

        invoice_line_vals = []
        for reg in uninvoiced_registrations:
            for line in reg.line_ids:
                invoice_line_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": f"Fees: {line.course_id.name} - {self.name}",
                            "quantity": 1,
                            "price_unit": line.registration_fee,
                        },
                    )
                )

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_id.id,
                "student_id": self.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_line_vals,
            }
        )
        uninvoiced_registrations.write({"is_invoiced": True, "invoice_id": invoice.id})

        return {
            "name": self.env._("New Student Invoice"),
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": invoice.id,
            "type": "ir.actions.act_window",
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Overridden create to handle auto-naming and sequences."""
        for vals in vals_list:
            if vals.get("admission_no", "New") == "New":
                vals["admission_no"] = (
                    self.env["ir.sequence"].next_by_code("college.student") or "New"
                )
            first = vals.get("first_name", "")
            last = vals.get("last_name", "")
            if not vals.get("name"):
                vals["name"] = f"{first} {last}".strip() or "New Student"
        return super().create(vals_list)

    @api.model
    def get_student_dashboard_stats(self):
        """Return statistics for the Odoo dashboard widget."""
        return {
            "total_students": self.search_count([]),
            "active_students": self.search_count([("status", "=", "active")]),
            "total_unpaid": sum(
                self.search([("student_credit", ">", 0)]).mapped("student_credit")
            ),
            "currency_symbol": self.env.company.currency_id.symbol or "$",
        }