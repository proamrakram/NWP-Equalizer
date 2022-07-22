try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import find_packages, setup

config = {
    "description": "NWP backend App",
    "version": "0.1",
    "install_requires": [
        "certifi",
        "chardet",
        "Click",
        "colorama",
        "nose",
        "idna",
        "itsdangerous",
        "Jinja2",
        "MarkupSafe",
        "pyasn1",
        "Pygments",
        "flask",
        "sqlalchemy",
        "mysqlclient",
        "requests",
        "flask_jsontools",
        "ldap3",
        "urllib3",
        "flask_sqlalchemy",
        "flask-migrate",
        "Flask_admin",
        "Werkzeug",
        "WTForms",
        "python-dotenv",
        "flask_weasyprint",
        "flask_wtf",
        "Flask-Mail",
    ],
    "packages": find_packages(),
    "scripts": [],
    "name": "NWP",
}

setup(**config)
