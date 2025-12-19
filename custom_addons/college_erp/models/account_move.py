from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    # ربط الفاتورة بالطالب
    student_id = fields.Many2one(
        'college.student', 
        string="Student", 
        help="The student associated with this invoice"
    )