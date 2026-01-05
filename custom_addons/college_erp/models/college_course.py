from odoo import models, fields


class CollegeCourse(models.Model):
    _name = "college.course"
    _description = "College Course"

    name = fields.Char(string="Course Name", required=True)
    code = fields.Char(string="Course Code", required=True)
    department_id = fields.Many2one("college.department", string="Department")
    unit_price = fields.Float(string="Registration Fee", required=True, default=0.0)
    active = fields.Boolean(default=True)
