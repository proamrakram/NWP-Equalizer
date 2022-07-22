import click
from flask.cli import with_appcontext, AppGroup


from nwpapp.model.model import (
    db,
    SensorStatus,
    LocStatus,
)


masters_cli = AppGroup("masters")


@masters_cli.command("ss")
@click.argument("data")
@with_appcontext
def add_sensorstatus_command(data):
    """Add new sensor status format <int status code>:<Status Description>"""
    sstatus = SensorStatus(
        Status=int(data.split(":")[0]), Description=data.split(":")[1]
    )
    db.session.add(sstatus)
    db.session.commit()
    click.echo(
        "Added Sensor Status - %s - to the database." % data.split(":")[1]
    )


@masters_cli.command("ls")
@click.argument("data")
@with_appcontext
def add_sensorstatus_command(data):
    """Add new location status format <int status code>:<Status Description>"""
    sstatus = LocStatus(
        LocStatus=int(data.split(":")[0]), Description=data.split(":")[1]
    )
    db.session.add(sstatus)
    db.session.commit()
    click.echo(
        "Added Location Status - %s - to the database." % data.split(":")[1]
    )
