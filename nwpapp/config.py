import os

class base_config(object):

    SECRET_KEY = "e7742915da26437b98ac7bb56bb45bde"
    # SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://root:Maisara@0815@localhost:3307/param"
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://proamrakram:amr123@localhost:3306/proamrakram'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LDAP_SERVER = "npcdc2.robian.local"
    LDAP_DOMAIN = "ROBIAN"
    LDAP_AUTH_GROUP = "KPIDashboard"
    FLASK_ADMIN_SWATCH = "cerulean"
    LOGFILE = "G:/Python/مشروع الاخ تركي/log/nwpapp/nwpapp.log"
    LOGLEVEL = 30
    MAIL_SERVER = "mta1.naqua.com.sa"
    MAIL_PORT = "25"
    MAIL_USE_TLS = "0"
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""


class development_config(base_config):

    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://proamrakram:amr123@localhost:3306/proamrakram"
    SECRET_KEY = "secret"
    # MAIL_SERVER = "smtp.googlemail.com"
    # MAIL_PORT = "587"
    # MAIL_USE_TLS = "1"
    # MAIL_USERNAME = "abofidu"
    # MAIL_PASSWORD = "jihad2017"
    # MAIL_SERVER = os.environ.get("MAIL_SERVER")
    # MAIL_PORT = os.environ.get("MAIL_PORT")
    # MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    # MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    # MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")


class test_config(base_config):

    SQLALCHEMY_DATABASE_URI = "mysql+mysqldb://proamrakram:amr123@localhost:3306/proamrakram"
    SECRET_KEY = "secret"

