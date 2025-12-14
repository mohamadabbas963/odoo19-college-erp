from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Patient'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)

    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', tracking=True)

    tag_ids = fields.Many2many(
        'patient.tag',
        'patient_tag_rel',
        'patient_id',
        'tag_id',
        string='Tags'
    )

    is_minor = fields.Boolean(string='Is Minor', tracking=True)

    guardian = fields.Char(string='Guardian')

    weight = fields.Float(string='Weight', required=True)

    @api.constrains('is_minor', 'guardian')
    def _check_guardian(self):
        for rec in self:
            if rec.is_minor and not rec.guardian:
                raise ValidationError("Guardian is required for minors.")

    def unlink(self):
        for rec in self:
            appointments = self.env['hospital.appointment'].search([
                ('patient_id', '=', rec.id),
                ('state', 'in', ['confirmed', 'done'])
            ])
            if appointments:
                raise UserError("Cannot delete patient with active appointments.")
        return super().unlink()
