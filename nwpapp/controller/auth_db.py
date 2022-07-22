from flask import current_app
from ldap3 import Server, Connection, ALL, NTLM, Reader
from ldap3.core import exceptions


def has_credentials(username, password):
    connection_attemps = 0
    while connection_attemps < 10:
        try:
            conn = Connection(
                Server(current_app.config["LDAP_SERVER"], use_ssl=True, get_info=ALL),
                user="\\".join((current_app.config["LDAP_DOMAIN"], username)),
                password=password,
                authentication=NTLM,
            )
            if not conn.bind():  # Check password
                return False
            person_record = (
                Reader(
                    conn,
                    "person",
                    "DC=" + current_app.config["LDAP_DOMAIN"] + ",DC=local",
                    "(sAMAccountName=" + username + ")",
                )
                .search()
                .pop()
            )
            groups = [
                value.split(",")[0].split("=")[1]
                for value in person_record.memberOf.value
            ]
            conn.unbind()
            return True  # all users allowed
        except (
            exceptions.LDAPSocketOpenError, 
            exceptions.LDAPSocketSendError
        ) as e:
            connection_attemps = connection_attemps + 1
            print(connection_attemps, "error in bind", e)
    return False
