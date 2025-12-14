from odoo import models, fields, api

class PatientTag(models.Model):
    _name = 'patient.tag'
    _description = 'Patient Tag'
    _order = 'sequence,id'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Tag name must be unique!')
    ]
