from .auth_cli import init_db_command, user_cli, group_cli
from .masters import masters_cli


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(user_cli)
    app.cli.add_command(group_cli)

    app.cli.add_command(masters_cli)
