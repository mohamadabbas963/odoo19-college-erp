from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError
from datetime import date

class CollegeStudent(models.Model):
    _name = "college.student"
    _description = "College Student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # الوراثة بالانتداب لجعل الطالب شريكاً تجارياً
    _inherits = {'res.partner': 'partner_id'}

    # 1. الحقل الرابط الأساسي
    partner_id = fields.Many2one(
        'res.partner', 
        required=True, 
        ondelete='cascade', 
        string="Partner Record"
    )

    # 2. الحقول الأكاديمية وصور الكانبان (إضافات ضرورية)
    # ربط الصورة من res.partner لكي تظهر في الكانبان
    image_128 = fields.Image(related='partner_id.image_128', readonly=False)
    image_1920 = fields.Image(related='partner_id.image_1920', readonly=False)
    
    # ربط حقل الاسم ليتم تحديثه في res.partner تلقائياً
    name = fields.Char(related='partner_id.name', readonly=False, store=True)

    admission_no = fields.Char(string="Admission Number", required=True, tracking=True)
    first_name = fields.Char(string="First Name", required=True, tracking=True)
    last_name = fields.Char(string="Last Name", required=True, tracking=True)
    
    # حقول التواصل
    student_email = fields.Char(string="Email", tracking=True)
    student_phone = fields.Char(string="Phone")
    student_mobile = fields.Char(string="Mobile")
    
    # الحقول المالية
    student_total_invoiced = fields.Monetary(string="Total Invoiced", compute="_compute_financials")
    student_credit = fields.Monetary(string="Total Amount Due", compute="_compute_financials")
    currency_id = fields.Many2one(related='partner_id.currency_id')
    
    gender = fields.Selection(
        [('male', 'Male'), ('female', 'Female')],
        string="Gender", required=True, tracking=True
    )
    admission_date = fields.Date(string="Admission Date", required=True, default=fields.Date.context_today)
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True)
    
    father_name = fields.Char(string="Father's Name")
    mother_name = fields.Char(string="Mother's Name")
    communication_address = fields.Text(string="Communication Address")

    # 3. العلاقات
    department_id = fields.Many2one('college.department', string="Department", tracking=True)
    attendance_ids = fields.One2many("college.attendance", "student_id", string="Attendance")
    fees_ids = fields.One2many("college.fees", "student_id", string="Fees")
    certificate_ids = fields.One2many("college.certificate", "student_id", string="Certificates")

    # 4. الحالة
    status = fields.Selection([
        ('new', 'New'), ('active', 'Active'),
        ('graduated', 'Graduated'), ('blocked', 'Blocked')
    ], string="Status", default="new", tracking=True)

    # 5. حقول العدادات
    attendance_count = fields.Integer(compute="_compute_counts")
    fees_count = fields.Integer(compute="_compute_counts")
    certificate_count = fields.Integer(compute="_compute_counts")

    @api.depends('partner_id.total_invoiced', 'partner_id.credit')
    def _compute_financials(self):
        for rec in self:
            rec.student_total_invoiced = rec.partner_id.total_invoiced
            rec.student_credit = rec.partner_id.credit
    
    # تحديث اسم الطالب والشريك عند تغيير الاسم الأول أو الأخير
    @api.onchange('first_name', 'last_name')
    def _onchange_student_name(self):
        self.name = f"{self.first_name or ''} {self.last_name or ''}".strip()

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                rec.age = today.year - rec.date_of_birth.year - \
                          ((today.month, today.day) < (rec.date_of_birth.month, rec.date_of_birth.day))
            else:
                rec.age = 0

    def _compute_counts(self):
        for rec in self:
            rec.attendance_count = len(rec.attendance_ids)
            rec.fees_count = len(rec.fees_ids)
            rec.certificate_count = len(rec.certificate_ids)

    def action_create_invoice(self):
        return {
            'name': 'Create Student Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'context': {
                'default_move_type': 'out_invoice',
                'default_partner_id': self.partner_id.id,
            },
            'target': 'current',
        }

    _sql_constraints = [
        ('admission_no_unique', 'UNIQUE (admission_no)', 'Admission Number must be unique.')
    ]

    def action_activate(self): self.write({'status': 'active'})
    def action_graduate(self): self.write({'status': 'graduated'})
    def action_block(self): self.write({'status': 'blocked'})