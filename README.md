# Naqua Water Parameters (nwp) Website 
## Table of Contents

- [About](#about)
- [Main Feartures](#main-features)
- [Quick Start](#quick-start)
- [Dependencies](#dependencies)
- [Docs](#docs)
- [Contributors](#contributors)
- [TODO](#todo)

## About ##
**NWP** is a web application to monitor and manage NAQUA's data collection for water parameters in fish PGO. It allows to login users that belong to the AD group `nwp`.

## Main Features ##
Here are just a few of the things that this app does:

- Present data at levels overview\sector\location
- forms to manage the setup for administrators
- process api GET and POST requests
- SQL to ORM.
- Complete documentation.
- Server.
- Authentication with Active Directory / LDAP

## Quick Start ##
### Installation: ###
- **For developers**:
    
    Development mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code. You can leave it running and just reload the browser page as you make changes.
        
    1. Use pip to **install** your project in the virtual environment.

            pip install -e .
        
    1. Set the **enviroment variables**: 
        
        For Linux and Mac:
        
        ```bash
        export FLASK_APP=nwpapp
        export FLASK_ENV=development
        ```
        For Windows cmd, use `set` instead of `export`:
        
        ```bash
        set FLASK_APP=nwpapp
        set FLASK_ENV=development
        ```
        For Windows PowerShell, use `$env:` instead of `export`:
        
        ```bash
        $env:FLASK_APP = "nwpapp"
        $env:FLASK_ENV = "development"
        ```
    1. Run the `init-db` command to **initialize the users auth database**:
    
        ```bash
        flask init-db
        Initialized the database.
        ```
        This will create tables in the param database in the defined server.
    1. Run the `user add-admin` command to **add an admin user to the database. This user can manage users and access privileges**:
    1. Run the `user add-superuser` command to **add an superuser to the database. THis user has admin rights, and can work with system setup**:
    
        ```bash
        flask user add-admin yourUser
        Added admin yourUser to the database.
        ```
        Whith that, there will be an admin user with username *yourUser* with rights to add new users, change privileges, add groups and set sectors for each group on the [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) page (only accesible after authentication).
        
            flask run
    
        You’ll see output similar to this:

            * Serving Flask app "nwpapp" (lazy loading)
            * Environment: development
            * Debug mode: on
            * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
            * Restarting with stat
            * Debugger is active!
            * Debugger PIN: 202-399-994

        Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in a browser and you should see the login page. You’re now running the **nwpapp** web application!


- **For end users**:


### Set up [NWP](): ###

    environment variables location :/var/www/nwpapp/config.py
        config variables for flask-mail and other variables should be placed here, eg:
            MAIL_SERVER="mta1.naqua.com.sa"
            MAIL_PORT="25"
            MAIL_USE_TLS="0"
            MAIL_USERNAME=""
            MAIL_PASSWORD=""

## Dependencies
- [pallets / **Flask**](https://www.palletsprojects.com/p/flask/)
- [nose-devs / **nose**](http://readthedocs.org/docs/nose/en/latest/)
- [zzzeek / **sqlalchemy**](http://sqlalchemy.org/develop.html)
- [flask / **flask-sqlalchemy**](http://sqlalchemy.org/develop.html)
- [jmcnamara / **XlsxWriter**](https://xlsxwriter.readthedocs.io/)
- [cannatag / **ldap3**](https://ldap3.readthedocs.io/)

## Docs
see `docs/` folder.

## Contributors

- [**Nassir Atik**](http://gitlab.naqua.com.sa/nassiratik) @nassiratik `Maintainer`

## TODO ##
* [ ] Forms to manage the infrastructure
* [ ] email and sms notifications
* [ ] Charts
* [ ] multi-level submenus





