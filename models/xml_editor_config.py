from odoo import models, fields, api
from lxml import etree
import json
import logging

_logger = logging.getLogger(__name__)


class XMLEditorConfig(models.Model):
    """Main configuration and storage model for XML Editor"""
    _name = 'xml.editor.config'
    _description = 'XML Editor Configuration'
    _rec_name = 'view_id'

    view_id = fields.Many2one(
        'ir.ui.view',
        string='View',
        required=True,
        ondelete='cascade',
        help='The Odoo view being edited'
    )
    view_type = fields.Selection(
        [('form', 'Form'),
         ('kanban', 'Kanban'),
         ('tree', 'Tree'),
         ('search', 'Search'),
         ('pivot', 'Pivot'),
         ('graph', 'Graph'),
         ('calendar', 'Calendar'),
         ('gantt', 'Gantt'),
         ('map', 'Map'),
         ('grid', 'Grid'),
         ('qweb', 'QWeb'),
         ('other', 'Other')],
        string='View Type',
        required=True
    )
    original_xml = fields.Text(
        string='Original XML',
        required=True,
        help='Original XML structure of the view'
    )
    modified_xml = fields.Text(
        string='Modified XML',
        help='Current modified XML structure'
    )
    is_modified = fields.Boolean(
        string='Is Modified',
        default=False,
        help='Indicates if the view has been modified'
    )
    last_modified_by = fields.Many2one(
        'res.users',
        string='Last Modified By',
        readonly=True
    )
    last_modified_date = fields.Datetime(
        string='Last Modified Date',
        readonly=True
    )
    created_date = fields.Datetime(
        string='Created Date',
        readonly=True,
        default=fields.Datetime.now
    )
    element_ids = fields.One2many(
        'xml.editor.element',
        'config_id',
        string='XML Elements'
    )
    change_log_ids = fields.One2many(
        'xml.editor.change.log',
        'config_id',
        string='Change History'
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Related Model',
        compute='_compute_model_id',
        store=True
    )
    description = fields.Text(
        string='Description',
        help='Description of modifications'
    )
    status = fields.Selection(
        [('draft', 'Draft'),
         ('active', 'Active'),
         ('archived', 'Archived')],
        string='Status',
        default='draft'
    )

    @api.depends('view_id')
    def _compute_model_id(self):
        """Compute related model from view"""
        for record in self:
            if record.view_id and record.view_id.model:
                record.model_id = self.env['ir.model'].search(
                    [('model', '=', record.view_id.model)], limit=1
                )

    @api.model
    def create(self, vals):
        """Create XML editor config with automatic XML extraction"""
        if 'view_id' in vals and not vals.get('original_xml'):
            view = self.env['ir.ui.view'].browse(vals['view_id'])
            vals['original_xml'] = view.arch_base or view.arch
            vals['view_type'] = view.type
        result = super().create(vals)
        result._parse_xml_elements()
        return result

    def write(self, vals):
        """Update with change logging"""
        if 'modified_xml' in vals:
            vals['is_modified'] = True
            vals['last_modified_by'] = self.env.user.id
            vals['last_modified_date'] = fields.Datetime.now()
            # Log the change
            for record in self:
                self.env['xml.editor.change.log'].create({
                    'config_id': record.id,
                    'previous_xml': record.modified_xml or record.original_xml,
                    'new_xml': vals['modified_xml'],
                    'changed_by': self.env.user.id,
                    'description': vals.get('description', 'Manual edit'),
                })
        result = super().write(vals)
        self._parse_xml_elements()
        return result

    def _parse_xml_elements(self):
        """Parse and store individual XML elements"""
        for record in self:
            try:
                xml_content = record.modified_xml or record.original_xml
                root = etree.fromstring(xml_content.encode('utf-8'))
                record.element_ids.unlink()
                self._process_xml_node(root, record, None, 0)
            except Exception as e:
                _logger.error(f"Error parsing XML: {str(e)}")

    def _process_xml_node(self, node, record, parent_element_id, depth):
        """Recursively process XML nodes"""
        element_vals = {
            'config_id': record.id,
            'tag_name': node.tag,
            'attributes': json.dumps(dict(node.attrib)),
            'text_content': (node.text or '').strip(),
            'depth': depth,
            'parent_element_id': parent_element_id,
            'order': list(node.getparent()).index(node) if node.getparent() is not None else 0,
        }
        element = self.env['xml.editor.element'].create(element_vals)
        for i, child in enumerate(node):
            self._process_xml_node(child, record, element.id, depth + 1)

    def apply_changes(self):
        """Apply modified XML to the actual view"""
        for record in self:
            if record.modified_xml and record.is_modified:
                try:
                    record.view_id.arch = record.modified_xml
                    record.status = 'active'
                    _logger.info(f"Applied changes to view {record.view_id.name}")
                except Exception as e:
                    _logger.error(f"Error applying changes: {str(e)}")

    def revert_to_original(self):
        """Revert to original XML"""
        for record in self:
            record.write({
                'modified_xml': record.original_xml,
                'is_modified': False,
                'description': 'Reverted to original'
            })

    def export_xml(self):
        """Export XML as file"""
        for record in self:
            xml_content = record.modified_xml or record.original_xml
            return {
                'content': xml_content,
                'filename': f"view_{record.view_id.id}.xml"
            }

    def import_xml(self, xml_content):
        """Import and validate XML"""
        try:
            etree.fromstring(xml_content.encode('utf-8'))
            self.write({
                'modified_xml': xml_content,
                'description': 'Imported from external source'
            })
            return True
        except Exception as e:
            _logger.error(f"Invalid XML: {str(e)}")
            return False
