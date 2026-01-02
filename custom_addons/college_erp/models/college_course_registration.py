from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CollegeCourseRegistration(models.Model):
    _name = 'college.course.registration'
    _description = 'Course Registration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    student_id = fields.Many2one('college.student', string='Student', required=True, tracking=True)
    department_id = fields.Many2one('college.department', string='Department', related='student_id.department_id',
                                    store=True)
    date = fields.Date(string='Registration Date', default=fields.Date.today)

    # حالة السجل: المسودة، بانتظار الإدارة، مقبول، ملغى
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # أسطر المواد المسجلة
    line_ids = fields.One2many('college.course.registration.line', 'registration_id', string='Courses')

    total_amount = fields.Float(string='Total Fees', compute='_compute_total_amount', store=True)
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    @api.depends('line_ids.price')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('price'))

    def action_submit(self):
        self.state = 'submitted'

    def action_confirm(self):
        # هنا يكمن دور الإدارة القوي في القبول وإنشاء الفاتورة
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("You cannot confirm a registration without courses!"))
            rec.state = 'confirmed'
            # (هنا سنضع كود إنشاء الفاتورة تلقائياً في الخطوة القادمة)

    def action_cancel(self):
        self.state = 'cancel'


class CollegeCourseRegistrationLine(models.Model):
    _name = 'college.course.registration.line'
    _description = 'Registration Line'

    registration_id = fields.Many2one('college.course.registration')
    course_id = fields.Many2one('college.course', string='Course', required=True)
    # جلب السعر تلقائياً بمجرد اختيار المادة (onchange)
    price = fields.Float(string='Price')

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            self.price = self.course_id.unit_price