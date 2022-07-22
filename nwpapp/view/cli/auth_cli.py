import click
from flask import g
from flask.cli import with_appcontext, AppGroup

from nwpapp.model.auth_model import db, User, Group, NSector


SECTORS = ["Sector1", "Sector2", "Samp", "Hatchery"]


def init_db():
    db.drop_all()
    db.create_all()
    for sectorname in SECTORS:
        sector = NSector(name=sectorname)
        db.session.add(sector)
        click.echo("Added %s to the database." % sectorname)
    db.session.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized auth database.")


user_cli = AppGroup("user")


@user_cli.command("add")
@click.argument("username")
@with_appcontext
def add_user_command(username):
    """Add new user to the database."""
    user = User(name=username, admin=False, active=True)
    db.session.add(user)
    db.session.commit()
    click.echo("Added %s to the database." % username)


@user_cli.command("add-admin")
@click.argument("username")
@with_appcontext
def add_admin_command(username):
    """Add new user to the database."""
    user = db.session.query(User).filter_by(name=username).first()
    if user is None:
        user = User(name=username, admin=True, active=True)
        db.session.add(user)
    else:
        user.admin = True
    db.session.commit()
    click.echo("Added admin %s to the database." % username)


@user_cli.command("add-superuser")
@click.argument("username")
@with_appcontext
def add_superuser_command(username):
    """Add new user to the database."""
    user = db.session.query(User).filter_by(name=username).first()
    if user is None:
        user = User(name=username, superuser=True, active=True)
        db.session.add(user)
    else:
        user.superuser = True
    db.session.commit()
    click.echo("Added superuser %s to the database." % username)


group_cli = AppGroup("group")


@group_cli.command("add")
@click.argument("groupname")
@with_appcontext
def add_user_command(groupname):
    """Add new group to the database."""
    group = Group(name=groupname)
    db.session.add(group)
    db.session.commit()
    click.echo("Added %s to the database." % groupname)
