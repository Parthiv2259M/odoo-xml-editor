{
    'name': 'Odoo XML Editor',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Visual XML Editor for all Odoo Web UI Pages',
    'description': '''
        Comprehensive XML Editor Module for Odoo
        ==========================================
        
        Features:
        - Edit XML structure of all web pages and views
        - Drag-and-drop reordering of elements
        - Add, remove, and edit XML elements
        - Live preview of changes
        - Import/export XML capabilities
        - Support for all view types (form, kanban, tree, search, etc.)
        - Database persistence of changes
        - Version control and rollback functionality
        - Syntax highlighting
        - Element validation
    ''',
    'author': 'Parthiv2259M',
    'website': 'https://github.com/Parthiv2259M/odoo-xml-editor',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/xml_editor_views.xml',
        'views/xml_editor_menu.xml',
    ],
    'static': {
        'description': 'Static files for XML Editor interface',
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
