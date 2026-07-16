# Odoo XML Editor Module

A comprehensive XML editor module for Odoo that provides visual editing capabilities for all web UI pages and views.

## Features

### Core Functionality
- ✅ **Visual XML Editor** - Edit XML structure with syntax highlighting
- ✅ **All View Types** - Support for form, kanban, tree, search, pivot, graph, calendar, gantt, map, grid, and QWeb views
- ✅ **Drag-and-Drop Reordering** - Easily reorder XML elements within the hierarchy
- ✅ **Element Management** - Add, remove, duplicate, and edit XML elements
- ✅ **Attribute Editing** - Modify element attributes with JSON support
- ✅ **Live Preview** - See changes in real-time
- ✅ **Import/Export** - Import and export XML configurations
- ✅ **Database Persistence** - All changes are stored in the database
- ✅ **Version Control** - Complete change history with rollback capabilities
- ✅ **Syntax Validation** - XML validation before applying changes
- ✅ **Multi-User Support** - Track who made changes and when

## Installation

1. Clone the module into your Odoo addons directory:
```bash
cd /path/to/odoo/addons
git clone https://github.com/Parthiv2259M/odoo-xml-editor.git xml_editor
```

2. Restart Odoo and update module list

3. Install the module:
   - Go to Apps
   - Search for "XML Editor"
   - Click "Install"

## Usage

### Getting Started

1. Navigate to **XML Editor** menu in Odoo
2. Click **View Configurations**
3. Click **Create** to add a new configuration
4. Select a view to edit
5. The original XML will be automatically loaded

### Editing XML

#### Method 1: Direct XML Editing
1. In the Modified XML tab, edit the XML directly
2. Use the ACE editor with syntax highlighting
3. Changes are validated in real-time

#### Method 2: Visual Element Editing
1. Use the Element Structure section to view the hierarchy
2. Click on elements to edit their attributes
3. Use buttons to add, remove, or duplicate elements

#### Reordering Elements
1. In the Element Structure tree, drag elements to new positions
2. Or use the "Order" field to specify position
3. Changes are applied immediately

### Managing Attributes

1. Select an element in the Element Structure
2. Click "Edit" to open the element form
3. Edit attributes in JSON format
4. Click "Update Attribute" or use the form fields

### Applying Changes

1. Click the **Apply Changes** button in the form header
2. The modified XML will be applied to the actual view
3. The status will change to "Active"

### Reverting Changes

1. Click the **Revert** button to go back to original XML
2. Or select a specific change from **Change History**
3. Click **Rollback to This Version**

### Viewing Change History

1. Navigate to **XML Editor** > **Change History**
2. See all modifications with user and timestamp
3. Click any change to view details
4. Use **Rollback** to revert to that version

## Data Models

### xml.editor.config
Main configuration model storing XML and metadata:
- `view_id` - Link to ir.ui.view
- `view_type` - Type of view (form, kanban, etc.)
- `original_xml` - Unmodified XML backup
- `modified_xml` - Current XML content
- `is_modified` - Flag indicating modifications
- `status` - Draft/Active/Archived
- `element_ids` - Related elements
- `change_log_ids` - Modification history

### xml.editor.element
Individual XML element representation:
- `config_id` - Parent configuration
- `tag_name` - XML tag (form, field, group, etc.)
- `attributes` - JSON formatted attributes
- `text_content` - Element text content
- `depth` - Hierarchy depth
- `order` - Position among siblings
- `parent_element_id` - Parent element reference
- `child_element_ids` - Child elements

### xml.editor.change.log
Change tracking and audit trail:
- `config_id` - Related configuration
- `previous_xml` - Previous XML state
- `new_xml` - New XML state
- `changed_by` - User who made change
- `created_date` - When change was made
- `description` - Change description
- `change_type` - Type of change

## REST API Endpoints

### Views
- `GET /xml-editor/views` - Get all available views
- `GET /xml-editor/view/<view_id>` - Get view editor

### Configuration
- `GET /xml-editor/config/<config_id>` - Get configuration details
- `POST /xml-editor/config/<config_id>/xml` - Update XML content
- `POST /xml-editor/config/<config_id>/apply` - Apply changes
- `POST /xml-editor/config/<config_id>/revert` - Revert changes
- `GET /xml-editor/config/<config_id>/export` - Export XML
- `POST /xml-editor/config/<config_id>/import` - Import XML

### Change History
- `GET /xml-editor/config/<config_id>/history` - Get change history
- `POST /xml-editor/config/<config_id>/history/<change_id>/rollback` - Rollback change

### Elements
- `POST /xml-editor/element/<element_id>/move` - Move/reorder element
- `POST /xml-editor/element/<element_id>/attribute` - Update attribute
- `POST /xml-editor/element/<element_id>/duplicate` - Duplicate element
- `POST /xml-editor/element/<element_id>/delete` - Delete element

## Security

- Users with basic access can view and edit XML configurations
- System administrators have full access including deletion rights
- Changes are tracked with user information for audit purposes
- All changes are logged in the change history

## Permissions

```
access_xml_editor_config_user       - User read/write access to XML configs
access_xml_editor_element_user      - User read/write access to elements
access_xml_editor_change_log_user   - User read-only access to change log
access_xml_editor_config_admin      - Admin full access to XML configs
access_xml_editor_element_admin     - Admin full access to elements
access_xml_editor_change_log_admin  - Admin full access to change log
```

## Development

### Project Structure
```
odoo-xml-editor/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── xml_editor_config.py      - Main configuration model
│   ├── xml_editor_element.py     - Element model
│   └── xml_editor_change_log.py  - Change tracking model
├── controllers/
│   ├── __init__.py
│   └── xml_editor_controller.py  - REST API endpoints
├── views/
│   ├── xml_editor_views.xml      - UI view definitions
│   └── xml_editor_menu.xml       - Menu structure
├── security/
│   └── ir.model.access.csv       - Access control rules
├── static/
│   └── description/
│       └── icon.png              - Module icon
└── README.md
```

### Adding New Features

1. **Custom XML Validators** - Extend `xml_editor_config.py` with custom validation logic
2. **Import Formats** - Add support for different XML source formats
3. **Live Preview** - Add a web interface for real-time preview
4. **Bulk Operations** - Create batch operations for multiple views
5. **XML Diff Viewer** - Add visual diff between versions

## Troubleshooting

### XML Validation Errors
- Check for unclosed tags
- Ensure all attributes are properly quoted
- Validate against XML schema

### Changes Not Applying
- Verify XML syntax is correct
- Check user permissions
- Review error logs in Odoo console

### Performance Issues
- Limit the number of changes in history (archive old records)
- Clear unnecessary element records
- Optimize database indexes

## License

LGPL-3 - See LICENSE file for details

## Author

Parthiv2259M - https://github.com/Parthiv2259M

## Support

For issues, feature requests, or contributions:
- GitHub Issues: https://github.com/Parthiv2259M/odoo-xml-editor/issues
- Pull Requests: https://github.com/Parthiv2259M/odoo-xml-editor/pulls

## Changelog

### Version 1.0.0 (2026-07-16)
- Initial release
- Core XML editing functionality
- Element management
- Change history and rollback
- REST API endpoints
- Multi-user support
- All view types support
