# -*- coding: utf-8 -*-
{
    "name": """Gantt Native Web view""",
    "summary": """Added support Gantt Chart Widget View""",
    "category": "Project",
    "images": ['static/description/icon.png'],
    "version": "11.18.3.16.0",
    "description": """
        Update 1: python 3.6.3 and click to gantt line
        Fix: momentjs fix
        Update 2: Calendar
    """,

    "author": "Viktor Vorobjov",
    "license": "OPL-1",
    "website": "https://straga.github.io",
    "support": "vostraga@gmail.com",
    "price": 250.00,
    "currency": "EUR",
    
    "depends": [
        "web", "web_widget_time_delta"
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/web_gantt_src.xml',
    ],
    "qweb": [
        'static/src/xml/*.xml',

    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
    "application": False,
}
