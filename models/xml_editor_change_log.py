from odoo import models, fields


class XMLEditorChangeLog(models.Model):
    """Track changes made to XML views"""
    _name = 'xml.editor.change.log'
    _description = 'XML Editor Change Log'
    _order = 'created_date desc'

    config_id = fields.Many2one(
        'xml.editor.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )
    previous_xml = fields.Text(
        string='Previous XML',
        required=True
    )
    new_xml = fields.Text(
        string='New XML',
        required=True
    )
    changed_by = fields.Many2one(
        'res.users',
        string='Changed By',
        required=True,
        readonly=True
    )
    created_date = fields.Datetime(
        string='Change Date',
        readonly=True,
        default=fields.Datetime.now
    )
    description = fields.Text(
        string='Change Description',
        help='Description of what was changed'
    )
    change_type = fields.Selection(
        [('add', 'Added Element'),
         ('delete', 'Deleted Element'),
         ('modify', 'Modified Element'),
         ('reorder', 'Reordered'),
         ('import', 'Imported'),
         ('batch', 'Batch Edit')],
        string='Change Type',
        default='batch'
    )

    def rollback(self):
        """Rollback to this previous version"""
        self.config_id.write({
            'modified_xml': self.previous_xml,
            'description': f'Rolled back to change from {self.changed_by.name}'
        })
