from odoo import models, fields, api
import json


class XMLEditorElement(models.Model):
    """Individual XML element model for hierarchical structure"""
    _name = 'xml.editor.element'
    _description = 'XML Editor Element'
    _order = 'config_id, depth, order'

    config_id = fields.Many2one(
        'xml.editor.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )
    tag_name = fields.Char(
        string='Tag Name',
        required=True,
        help='XML tag name (e.g., form, field, group)'
    )
    attributes = fields.Text(
        string='Attributes',
        help='JSON format attributes'
    )
    text_content = fields.Text(
        string='Text Content',
        help='Text content of the element'
    )
    depth = fields.Integer(
        string='Depth',
        default=0,
        help='Hierarchy depth in XML tree'
    )
    order = fields.Integer(
        string='Order',
        default=0,
        help='Position among siblings'
    )
    parent_element_id = fields.Many2one(
        'xml.editor.element',
        string='Parent Element',
        ondelete='cascade'
    )
    child_element_ids = fields.One2many(
        'xml.editor.element',
        'parent_element_id',
        string='Child Elements'
    )
    created_date = fields.Datetime(
        string='Created Date',
        readonly=True,
        default=fields.Datetime.now
    )

    @api.model
    def get_attributes_dict(self):
        """Parse attributes JSON to dictionary"""
        try:
            return json.loads(self.attributes) if self.attributes else {}
        except:
            return {}

    def update_attribute(self, attr_name, attr_value):
        """Update a specific attribute"""
        attrs = self.get_attributes_dict()
        attrs[attr_name] = attr_value
        self.attributes = json.dumps(attrs)

    def remove_attribute(self, attr_name):
        """Remove a specific attribute"""
        attrs = self.get_attributes_dict()
        attrs.pop(attr_name, None)
        self.attributes = json.dumps(attrs)

    def move_to_position(self, new_order, new_parent_id=None):
        """Reorder element or move to different parent"""
        self.write({
            'order': new_order,
            'parent_element_id': new_parent_id or self.parent_element_id.id,
        })
        self.config_id._parse_xml_elements()

    def duplicate(self, new_parent_id=None):
        """Duplicate this element"""
        vals = {
            'config_id': self.config_id.id,
            'tag_name': self.tag_name,
            'attributes': self.attributes,
            'text_content': self.text_content,
            'depth': self.depth,
            'parent_element_id': new_parent_id or self.parent_element_id.id,
        }
        new_element = self.create(vals)
        # Duplicate children
        for child in self.child_element_ids:
            child.duplicate(new_element.id)
        return new_element

    def delete_element(self):
        """Delete element and refresh XML"""
        config = self.config_id
        self.unlink()
        config._parse_xml_elements()
