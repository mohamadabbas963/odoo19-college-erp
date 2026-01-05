from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date


class CollegeStudent(models.Model):
    _name = "college.student"
    _description = "College Student"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # الوراثة بالانتداب لجعل الطالب شريكاً تجارياً
    _inherits = {"res.partner": "partner_id"}

    # 1. الحقول الأساسية والربط مع الشريك
    partner_id = fields.Many2one(
        "res.partner", required=True, ondelete="cascade", string="Partner Record"
    )
    current_classroom_id = fields.Many2one(
        "college.classroom",
        string="Allocated Classroom",
        help="القاعة الدراسية المسكن فيها الطالب حالياً",
    )

    # حقول الصور مرتبطة بالشريك لتظهر في الكانبان والنموذج
    image_128 = fields.Image(related="partner_id.image_128", readonly=False)
    image_1920 = fields.Image(related="partner_id.image_1920", readonly=False)

    admission_no = fields.Char(
        string="Admission Number", required=True, tracking=True, default="New"
    )
    first_name = fields.Char(string="First Name", required=True, tracking=True)
    last_name = fields.Char(string="Last Name", required=True, tracking=True)

    # 2. حقول التواصل والمعلومات الشخصية
    student_email = fields.Char(string="Student Email", tracking=True)
    student_phone = fields.Char(string="Student Phone")
    student_mobile = fields.Char(string="Mobile")
    gender = fields.Selection(
        [("male", "Male"), ("female", "Female")],
        string="Gender",
        required=True,
        tracking=True,
    )
    admission_date = fields.Date(
        string="Admission Date", required=True, default=fields.Date.context_today
    )
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    communication_address = fields.Text(string="Communication Address")

    # 3. العلاقات والحالة
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
        string="Status",
        default="new",
        tracking=True,
    )

    # 4. الحقول المالية (محسوبة من الشريك)
    currency_id = fields.Many2one(related="partner_id.currency_id")
    student_total_invoiced = fields.Monetary(
        string="Student Total Invoiced", compute="_compute_financials", store=True
    )
    student_credit = fields.Monetary(
        string="Student Balance Due", compute="_compute_financials", store=True
    )

    # 5. الروابط والجداول (One2many)
    attendance_ids = fields.One2many(
        "college.attendance.line", "student_id", string="Attendance"
    )
    fees_ids = fields.One2many("college.fees", "student_id", string="Fees")
    certificate_ids = fields.One2many(
        "college.certificate", "student_id", string="Certificates"
    )

    # 6. حقول العدادات (Smart Buttons Counters)
    attendance_count = fields.Integer(compute="_compute_counts")
    fees_count = fields.Integer(compute="_compute_counts")
    certificate_count = fields.Integer(compute="_compute_counts")
    appointment_count = fields.Integer(compute="_compute_counts")
    registration_count = fields.Integer(compute="_compute_counts")
    exam_result_count = fields.Integer(compute="_compute_counts")

    # --- القيود (Constraints) ---
    _sql_constraints = [
        (
            "admission_no_unique",
            "UNIQUE (admission_no)",
            "Admission Number must be unique.",
        )
    ]

    # --- الدوال المحسوبة (Compute Methods) ---

    @api.depends("partner_id.total_invoiced", "partner_id.credit")
    def _compute_financials(self):
        for rec in self:
            rec.student_total_invoiced = rec.partner_id.total_invoiced
            rec.student_credit = rec.partner_id.credit

    @api.depends("date_of_birth")
    def _compute_age(self):
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
        """دالة موحدة لحساب جميع العدادات لتقليل الضغط على قاعدة البيانات"""
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)
            rec.fees_count = len(rec.fees_ids)
            rec.certificate_count = len(rec.certificate_ids)

            # حساب المواعيد والتسجيلات من خلال البحث في الموديلات الأخرى
            rec.appointment_count = self.env[
                "college.student.appointment"
            ].search_count([("student_id", "=", rec.id)])
            rec.registration_count = self.env[
                "college.course.registration"
            ].search_count([("student_id", "=", rec.id)])
            rec.exam_result_count = self.env["college.exam.result"].search_count(
                [("student_id", "=", rec.id)]
            )

    # --- الدوال التفاعلية (Onchange & Actions) ---

    @api.onchange("first_name", "last_name")
    def _onchange_student_name(self):
        self.name = f"{self.first_name or ''} {self.last_name or ''}".strip()

    def action_activate(self):
        self.write({"status": "active"})

    def action_graduate(self):
        for rec in self:
            # التحقق من آخر نتيجة امتحانات
            last_result = self.env["college.exam.result"].search(
                [("student_id", "=", rec.id)], order="exam_date desc", limit=1
            )

            if not last_result:
                raise UserError(_("لا يمكن تخرج طالب ليس لديه سجل نتائج امتحانات."))

            if last_result.status != "pass":
                raise UserError(
                    _("لا يمكن تخرج الطالب لأن حالته الأكاديمية الحالية هي: راسب.")
                )

            rec.write({"status": "graduated"})

    def action_block(self):
        self.write({"status": "blocked"})

    def action_view_appointments(self):
        return {
            "name": _("Academic Appointments"),
            "type": "ir.actions.act_window",
            "res_model": "college.student.appointment",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }

    def action_view_exam_results(self):
        self.ensure_one()
        return {
            "name": _("Exam Results"),
            "type": "ir.actions.act_window",
            "res_model": "college.exam.result",
            "view_mode": "list,form",
            "domain": [("student_id", "=", self.id)],
            "context": {"default_student_id": self.id},
        }

    def action_view_student_invoices(self):
        self.ensure_one()
        return {
            "name": "Student Invoices",
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
        self.ensure_one()
        # البحث عن التسجيلات التي لم تصدر لها فاتورة بعد
        uninvoiced_registrations = self.env["college.course.registration"].search(
            [
                ("student_id", "=", self.id),
                ("state", "=", "confirmed"),
                ("is_invoiced", "=", False),
            ]
        )

        # إذا لم نجد تسجيلات جديدة، نفتح قائمة الفواتير الموجودة بدلاً من إظهار خطأ
        if not uninvoiced_registrations:
            return {
                "name": _("Student Invoices"),
                "view_mode": "list,form",
                "res_model": "account.move",
                "type": "ir.actions.act_window",
                "domain": [
                    ("partner_id", "=", self.partner_id.id),
                    ("move_type", "=", "out_invoice"),
                ],
                "context": {"default_move_type": "out_invoice"},
                "help": _(
                    '<p class="o_view_nocontent_smiling_face">لا توجد فواتير جديدة، وهذه هي سجلات الفواتير السابقة.</p>'
                ),
            }

        # الكود الأصلي لإنشاء الفاتورة (في حال وجود تسجيلات جديدة)
        invoice_line_vals = []
        for reg in uninvoiced_registrations:
            for line in reg.line_ids:
                invoice_line_vals.append(
                    (
                        0,
                        0,
                        {
                            "name": f"Fees for: {line.course_id.name} - {self.name}",
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
            "name": _("New Student Invoice"),
            "view_mode": "form",
            "res_model": "account.move",
            "res_id": invoice.id,
            "type": "ir.actions.act_window",
        }

    # --- الدوال الأساسية للنظام (CRUD) ---

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("admission_no", "New") == "New":
                vals["admission_no"] = (
                    self.env["ir.sequence"].next_by_code("college.student") or "New"
                )

            first = vals.get("first_name", "")
            last = vals.get("last_name", "")
            combined_name = f"{first} {last}".strip()

            if not vals.get("name"):
                vals["name"] = combined_name or "New Student"

        return super(CollegeStudent, self).create(vals_list)

    @api.model
    def get_student_dashboard_stats(self):
        """
        الغاية: جلب أرقام إحصائية عامة للكلية لعرضها في أعلى شاشة الطلاب.
        تعمل هذه الدالة عند فتح واجهة الكانبان لتحديث الأرقام لحظياً.
        """
        return {
            "total_students": self.search_count([]),
            "active_students": self.search_count([("status", "=", "active")]),
            "total_unpaid": sum(
                self.search([("student_credit", ">", 0)]).mapped("student_credit")
            ),
            "currency_symbol": self.env.company.currency_id.symbol or "$",
        }
