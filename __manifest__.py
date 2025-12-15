# -*- coding: utf-8 -*-

{
    'name': "Project Timeline",
    'summary': "Project Timeline",
    "description": """
    This module extends the project management functionalities by integrating
    timeline features, allowing users to track project progress over time.
    """,
    'author': "AbdoPrDZ",
    'website': "https://github.com/AbdoPrDZ",
    'license': 'AGPL-3',
    'category': 'Project',
    'version': '1.0.0',
    'depends': ['base', 'web', 'mail', 'project', 'hr', 'app_access'],
    "data": [
        'security/ir.model.access.csv',
        'views/project.xml',
        'views/project_task.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
