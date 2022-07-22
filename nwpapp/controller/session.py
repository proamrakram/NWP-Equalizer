from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import click
from flask import current_app, g
from flask.cli import with_appcontext, AppGroup


from nwpapp.model.model import (
    engine,
    Base,
    Reading,
    Controller,
    Sensor,
    SensorType,
    SensorStatus,
    Location,
    LocStatus,
    ControllerStatus,
    Model,
)


# engine = create_engine('mssql+pymssql://intelliview:intelliview@naqssrs:1433/intelliviewdbDW')


# engine = create_engine('mysql://nassir:naqua@123@localhost:3307/param')


def get_Session():

    session = sessionmaker(bind=engine)
    if "ds" not in g:
        g.ds = session()
        return g.ds
    if g.ds is None:
        g.ds = session()
        return g.ds

        # if g.ds is None:
        #     g.ds = session()
        #     return session()


def get_Session2():

    session = sessionmaker(bind=engine)
    g.dss = session()
    return g.dss


def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@click.command("init-main-db")
@with_appcontext
def init_main_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized main database.")


masters_cli = AppGroup("masters")


@masters_cli.command("ss")
@click.argument("data")
@with_appcontext
def add_sensorstatus_command(data):
    """Add new sensor status format <int status code>:<Status Description>"""
    dsession = get_Session()

    sstatus = SensorStatus(
        Status=int(data.split(":")[0]), Description=data.split(":")[1]
    )
    dsession.add(sstatus)
    dsession.commit()
    dsession.close()
    click.echo(
        "Added Sensor Status - %s - to the database." % data.split(":")[1]
    )


@masters_cli.command("ls")
@click.argument("data")
@with_appcontext
def add_sensorstatus_command(data):
    """Add new location status format <int status code>:<Status Description>"""
    dsession = get_Session()

    sstatus = LocStatus(
        LocStatus=int(data.split(":")[0]), Description=data.split(":")[1]
    )
    dsession.add(sstatus)
    dsession.commit()
    dsession.close()
    click.echo(
        "Added Location Status - %s - to the database." % data.split(":")[1]
    )


def close_mdb(e=None):
    ds = g.pop("ds", None)
    if ds is not None:
        ds.commit()
        ds.close()


def init_app(app):
    app.teardown_appcontext(close_mdb)
    app.cli.add_command(init_main_db_command)
    app.cli.add_command(masters_cli)
