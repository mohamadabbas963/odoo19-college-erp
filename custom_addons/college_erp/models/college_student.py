from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from datetime import date


class CollegeStudent(models.Model):
    _name = "college.student"
    _description = "College Student"

    # ======== CONSTRAINTS ========
    _sql_constraints = [
        ('admission_no_unique', 'UNIQUE (admission_no)', 'Admission Number must be unique.')
    ]
    # ===========================

    # --------- ODOO MODEL SETUP ----------
    _rec_name = "name"
    _order = "admission_no"

    # --------- STATUSBAR ----------
    status = fields.Selection(
        [
            ('new', 'New'),
            ('active', 'Active'),
            ('graduated', 'Graduated'),
            ('blocked', 'Blocked'),
        ],
        string="Status",
        default="new",
        tracking=True,
    )

    # ---------- BASIC FIELDS ----------
    admission_no = fields.Char(string="Admission Number", required=True)
    first_name = fields.Char(string="First Name", required=True)
    last_name = fields.Char(string="Last Name", required=True)
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender",
        required=True
    )
    admission_date = fields.Date(string="Admission Date", required=True)
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    communication_address = fields.Text(string="Communication Address", required=True)
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")

    # ======= CALCULATED FIELD =======
    age = fields.Integer(string="Age", compute="_compute_age", store=True)

    # ---------- ADDRESS FIELDS ----------
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one('res.country', string='Country')
    country_code = fields.Char(related='country_id.code', string="Country Code", store=True)
    same_as_communication = fields.Boolean(string="Same as Communication", default=True)

    image_1920 = fields.Image()

    # ---------- RELATION FIELDS (Many2one) ----------
    department_id = fields.Many2one('college.department', string="Department")
    partner_id = fields.Many2one(
        'res.partner',
        string="Related Partner",
        ondelete='set null',
        help="Linked partner or contact record."
    )

    # ---------- RELATION FIELDS (One2many) ----------
    attendance_ids = fields.One2many(
        "college.attendance",
        "student_id",
        string="Attendance Records"
    )

    fees_ids = fields.One2many(
        "college.fees",
        "student_id",
        string="Fees Records"
    )

    certificate_ids = fields.One2many(
        "college.certificate",
        "student_id",
        string="Certificates"
    )

    # ---------- COMPUTED NAME ----------
    name = fields.Char(
        string="Student Name",
        compute="_compute_name",
        store=True,
        readonly=False
    )

    # ---------- SMART BUTTON COUNTERS (مطلوبة في الـ XML) ----------
    attendance_count = fields.Integer(
        string="Attendance Count",
        compute="_compute_attendance_count"
    )
    fees_count = fields.Integer(
        string="Fees Count",
        compute="_compute_fees_count"
    )
    certificate_count = fields.Integer(
        string="Certificates Count",
        compute="_compute_certificate_count"
    )

    # --------------------------
    # COMPUTE METHODS
    # --------------------------
    @api.depends('first_name', 'last_name', 'admission_no')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.first_name or ''} {rec.last_name or ''} [{rec.admission_no or ''}]"

    @api.depends('admission_date')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.admission_date:
                # حساب الفرق بالسنوات
                rec.age = today.year - rec.admission_date.year - \
                          ((today.month, today.day) < (rec.admission_date.month, rec.admission_date.day))
            else:
                rec.age = 0

    @api.depends('attendance_ids')
    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = self.env['college.attendance'].search_count([('student_id', '=', rec.id)])

    @api.depends('fees_ids')
    def _compute_fees_count(self):
        for rec in self:
            rec.fees_count = self.env['college.fees'].search_count([('student_id', '=', rec.id)])

    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        for rec in self:
            rec.certificate_count = self.env['college.certificate'].search_count([('student_id', '=', rec.id)])

    # --------------------------
    # ONCHANGE METHODS
    # --------------------------
    @api.onchange('same_as_communication')
    def _onchange_same_as_communication(self):
        if self.same_as_communication:
            self.street = self.communication_address

    # --------------------------
    # CONSTRAINTS
    # --------------------------
    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError("Please enter a valid email address.")

    # --------------------------
    # WORKFLOW ACTIONS (STATUSBAR)
    # --------------------------
    def action_activate(self):
        for rec in self:
            if rec.status == 'active':
                continue  # الطالب مفعل مسبقاً، لا نفعل شيء
            rec.status = 'active'

    def action_graduate(self):
        for rec in self:
            if rec.status != 'active':
                # بدل رفع خطأ، يمكن تخطي أو إعلام المستخدم بطريقة مرنة
                continue
            rec.status = 'graduated'

    def action_block(self):
        for rec in self:
            if rec.status in ['blocked']:
                continue  # الطالب مفعل مسبقاً كـ blocked
            rec.status = 'blocked'

