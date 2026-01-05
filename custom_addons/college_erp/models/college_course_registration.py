# -*- coding: utf-8 -*-
""" University Management System """
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CollegeCourseRegistration(models.Model):
    _name = "college.course.registration"
    _description = "Course Registration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(
        string="Order Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env._("New"),
    )
    student_id = fields.Many2one(
        "college.student", string="Student", required=True, tracking=True
    )
    department_id = fields.Many2one(
        "college.department",
        string="Department",
        related="student_id.department_id",
        store=True,
    )
    date = fields.Date(string="Registration Date", default=fields.Date.today)

    # حقل الربط المالي الهام
    is_invoiced = fields.Boolean(
        string="Invoiced", default=False, copy=False, tracking=True
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("confirmed", "Confirmed"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    line_ids = fields.One2many(
        "college.course.registration.line", "registration_id", string="Courses"
    )
    total_amount = fields.Float(
        string="Total Fees", compute="_compute_total_amount", store=True
    )
    invoice_id = fields.Many2one("account.move", string="Invoice", readonly=True)

    @api.depends("line_ids.price")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("price"))

    # دالة الترقيم التلقائي
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", self.env._("New")) == self.env._("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "college.course.registration"
                ) or self.env._("New")
        return super().create(vals_list)

    def action_submit(self):
        self.state = "submitted"

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(self.env._("You cannot confirm a registration without courses!"))
            rec.state = "confirmed"

    def action_cancel(self):
        self.state = "cancel"


class CollegeCourseRegistrationLine(models.Model):
    _name = "college.course.registration.line"
    _description = "Registration Line"

    registration_id = fields.Many2one("college.course.registration", ondelete="cascade")
    course_id = fields.Many2one("college.course", string="Course", required=True)

    # حقول السعر
    price = fields.Float(string="Price")
    # هذا الحقل هو الذي ستقرأه دالة الفوترة في ملف الطالب
    registration_fee = fields.Float(string="Fee", related="price", store=True)

    @api.onchange("course_id")
    def _onchange_course_id(self):
        if self.course_id:
            # تأكد أن اسم الحقل في موديل الكورس هو unit_price
            self.price = self.course_id.unit_price or 0.0
