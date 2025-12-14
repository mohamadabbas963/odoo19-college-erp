from odoo import models, fields, api

class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'

    reference = fields.Char(string='Reference', default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=False, ondelete='cascade')
    date_appointment = fields.Datetime(string='Date Appointment')
    note = fields.Text(string='Note')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft', tracking=True)

    appointment_line_ids = fields.One2many(
        'hospital.appointment.line', 'appointment_id', string="Lines"
    )

    total_qty = fields.Float(
        compute='_compute_total_qty',
        string="Total Quantity",
        store=True
    )

    date_of_birth = fields.Date(related='patient_id.date_of_birth', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.appointment')
        return super().create(vals_list)

    @api.depends('appointment_line_ids.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.appointment_line_ids.mapped('qty'))

    def name_get(self):
        res = []
        for rec in self:
            name = f"[{rec.reference}] {rec.patient_id.name}"
            res.append((rec.id, name))
        return res

    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(
            ['|', ('reference', operator, name), ('patient_id.name', operator, name)] + args,
            limit=limit
        )
        return recs.name_get()

    def action_confirm(self):
        self.state = 'confirmed'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'


class HospitalAppointmentLine(models.Model):
    _name = 'hospital.appointment.line'
    _description = 'Hospital Appointment Line'

    appointment_id = fields.Many2one('hospital.appointment', string="Appointment")
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float(string='Quantity')
