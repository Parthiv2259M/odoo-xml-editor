from odoo import http
from odoo.http import request
import json
from lxml import etree
import logging

_logger = logging.getLogger(__name__)


class XMLEditorController(http.Controller):
    """REST API endpoints for XML Editor"""

    @http.route('/xml-editor/views', type='json', auth='user')
    def get_available_views(self):
        """Get all available views for editing"""
        views = request.env['ir.ui.view'].search([])
        return {
            'views': [{
                'id': view.id,
                'name': view.name,
                'type': view.type,
                'model': view.model,
            } for view in views]
        }

    @http.route('/xml-editor/view/<int:view_id>', type='json', auth='user')
    def get_view_editor(self, view_id):
        """Get or create XML editor config for a view"""
        view = request.env['ir.ui.view'].browse(view_id)
        editor_config = request.env['xml.editor.config'].search(
            [('view_id', '=', view_id)], limit=1
        )
        
        if not editor_config:
            editor_config = request.env['xml.editor.config'].create({
                'view_id': view_id,
                'view_type': view.type,
            })
        
        return {
            'id': editor_config.id,
            'view_id': view.id,
            'view_name': view.name,
            'view_type': view.type,
            'original_xml': editor_config.original_xml,
            'modified_xml': editor_config.modified_xml or editor_config.original_xml,
            'is_modified': editor_config.is_modified,
        }

    @http.route('/xml-editor/config/<int:config_id>', type='json', auth='user')
    def get_config_details(self, config_id):
        """Get detailed configuration with elements"""
        config = request.env['xml.editor.config'].browse(config_id)
        elements = self._build_element_tree(config.element_ids.filtered(lambda e: not e.parent_element_id))
        
        return {
            'id': config.id,
            'view_id': config.view_id.id,
            'view_name': config.view_id.name,
            'view_type': config.view_type,
            'original_xml': config.original_xml,
            'modified_xml': config.modified_xml or config.original_xml,
            'is_modified': config.is_modified,
            'elements': elements,
            'change_count': len(config.change_log_ids),
        }

    @http.route('/xml-editor/config/<int:config_id>/xml', type='json', auth='user', methods=['POST'])
    def update_xml(self, config_id, **post):
        """Update XML content"""
        config = request.env['xml.editor.config'].browse(config_id)
        new_xml = post.get('xml_content')
        description = post.get('description', 'Manual edit')
        
        try:
            # Validate XML
            etree.fromstring(new_xml.encode('utf-8'))
            config.write({
                'modified_xml': new_xml,
                'description': description,
            })
            return {'success': True, 'message': 'XML updated successfully'}
        except Exception as e:
            _logger.error(f"XML validation error: {str(e)}")
            return {'success': False, 'error': f'Invalid XML: {str(e)}'}

    @http.route('/xml-editor/config/<int:config_id>/apply', type='json', auth='user', methods=['POST'])
    def apply_changes(self, config_id):
        """Apply changes to the actual view"""
        config = request.env['xml.editor.config'].browse(config_id)
        try:
            config.apply_changes()
            return {'success': True, 'message': 'Changes applied successfully'}
        except Exception as e:
            _logger.error(f"Error applying changes: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/xml-editor/config/<int:config_id>/revert', type='json', auth='user', methods=['POST'])
    def revert_changes(self, config_id):
        """Revert to original XML"""
        config = request.env['xml.editor.config'].browse(config_id)
        config.revert_to_original()
        return {'success': True, 'message': 'Reverted to original XML'}

    @http.route('/xml-editor/config/<int:config_id>/export', type='json', auth='user')
    def export_xml(self, config_id):
        """Export XML"""
        config = request.env['xml.editor.config'].browse(config_id)
        result = config.export_xml()
        return result

    @http.route('/xml-editor/config/<int:config_id>/import', type='json', auth='user', methods=['POST'])
    def import_xml(self, config_id, **post):
        """Import XML"""
        config = request.env['xml.editor.config'].browse(config_id)
        xml_content = post.get('xml_content')
        success = config.import_xml(xml_content)
        if success:
            return {'success': True, 'message': 'XML imported successfully'}
        else:
            return {'success': False, 'error': 'Invalid XML format'}

    @http.route('/xml-editor/config/<int:config_id>/history', type='json', auth='user')
    def get_change_history(self, config_id, limit=20):
        """Get change history"""
        config = request.env['xml.editor.config'].browse(config_id)
        changes = config.change_log_ids[:limit]
        return {
            'changes': [{
                'id': change.id,
                'changed_by': change.changed_by.name,
                'created_date': change.created_date.isoformat(),
                'description': change.description,
                'change_type': change.change_type,
            } for change in changes]
        }

    @http.route('/xml-editor/config/<int:config_id>/history/<int:change_id>/rollback', type='json', auth='user', methods=['POST'])
    def rollback_change(self, config_id, change_id):
        """Rollback to specific change"""
        change = request.env['xml.editor.change.log'].browse(change_id)
        change.rollback()
        return {'success': True, 'message': 'Rolled back successfully'}

    @http.route('/xml-editor/element/<int:element_id>/move', type='json', auth='user', methods=['POST'])
    def move_element(self, element_id, **post):
        """Move element to new position or parent"""
        element = request.env['xml.editor.element'].browse(element_id)
        new_order = int(post.get('order', 0))
        new_parent_id = post.get('parent_id')
        
        element.move_to_position(new_order, new_parent_id)
        element.config_id._parse_xml_elements()
        return {'success': True, 'message': 'Element moved successfully'}

    @http.route('/xml-editor/element/<int:element_id>/attribute', type='json', auth='user', methods=['POST'])
    def update_element_attribute(self, element_id, **post):
        """Update element attribute"""
        element = request.env['xml.editor.element'].browse(element_id)
        attr_name = post.get('name')
        attr_value = post.get('value')
        
        element.update_attribute(attr_name, attr_value)
        element.config_id._parse_xml_elements()
        return {'success': True, 'message': 'Attribute updated successfully'}

    @http.route('/xml-editor/element/<int:element_id>/duplicate', type='json', auth='user', methods=['POST'])
    def duplicate_element(self, element_id):
        """Duplicate an element"""
        element = request.env['xml.editor.element'].browse(element_id)
        new_element = element.duplicate()
        element.config_id._parse_xml_elements()
        return {'success': True, 'element_id': new_element.id}

    @http.route('/xml-editor/element/<int:element_id>/delete', type='json', auth='user', methods=['POST'])
    def delete_element(self, element_id):
        """Delete an element"""
        element = request.env['xml.editor.element'].browse(element_id)
        config_id = element.config_id.id
        element.delete_element()
        return {'success': True, 'message': 'Element deleted successfully'}

    def _build_element_tree(self, root_elements):
        """Recursively build element tree"""
        result = []
        for element in root_elements:
            result.append({
                'id': element.id,
                'tag_name': element.tag_name,
                'attributes': element.get_attributes_dict() if hasattr(element, 'get_attributes_dict') else {},
                'text_content': element.text_content,
                'depth': element.depth,
                'order': element.order,
                'children': self._build_element_tree(element.child_element_ids),
            })
        return result
