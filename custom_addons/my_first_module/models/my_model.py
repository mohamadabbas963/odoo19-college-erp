from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(string='Name', required=True)
    value = fields.Integer(string='Value')

    @api.model
    def create(self, vals):
        _logger.info(f"Creating record with values: {vals}")
        return super(MyModel, self).create(vals)

    def write(self, vals):
        _logger.info(f"Updating record {self.id} with values: {vals}")
        return super(MyModel, self).write(vals)

    def unlink(self):
        _logger.info(f"Deleting record {self.id}")
        return super(MyModel, self).unlink()
