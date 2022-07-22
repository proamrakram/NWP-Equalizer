"""View module for the dashboard REST API.

This module defines how our JSON data is presented on the different URLs.
"""
from datetime import datetime as dt
import time, requests
from werkzeug.exceptions import abort
from sqlalchemy import func, literal, or_
from flask import Blueprint, jsonify, request, current_app

from nwpapp.view.auth import login_required
from nwpapp.controller.response_gzip import gzipped
from nwpapp.model.model import (
    db,
    Reading,
    Controller,
    ControllerStatus,
    Sensor,
    Sector,
    SensorStatus,
    SensorType,
    LocHourlyReading,
    Location,
    LocStatus,
    LocSummByType,
    SectorSummByType,
    ErrorLog,
    ParamRange,
    Notification,
)
from nwpapp.model.auth_model import User
from nwpapp.view.errors import bad_request
from . import sysOptions
from nwpapp.extensions import mail
from flask_mail import Message
from . import baselogger, debuglogger

bp = Blueprint("api", __name__, url_prefix="/api")

ACTION_ADD = 1
ACTION_UPDATE = 2
ACTION_DEL = 3


def get_round(val, dec):
    val_out = 0
    try:
        val_out = round(val, dec)
    except:
        pass
    return val_out


def get_table_parameters(parameter_names):
    parameters = []
    for name in parameter_names:
        parameters.append(
            {
                "title": name,
                "field": name,
                "width": 130,
                "headerFilter": "input",
            }
        )
    return parameters


@bp.route("/sensor_reading", methods=["POST"])
def sensor_reading():
    
    """adds sensor reading received as json in URL argument
        the received data contains controller ID, sensor id, list of readings in 
        key/value {readingtype:value}
        Returns response indicating successful write or error
    """
    if not sysOptions["allowReadings"]:
        return bad_request("System temporarily paused")
    
    data = request.get_json() or {}
    
    data_error = False
    
    msg = ""
    
    if "Controller" not in data:
        msg = msg + "No Controller,"
    if "Sensor" not in data:
        msg = msg + "No Sensor,"
    if "ReadingTime" not in data:
        msg = msg + "No Date,"
    if "value" not in data:
        msg = msg + "No value,"
    if not (msg == ""):
        return bad_request("Incomplete data submitted : " + msg)

    sensor_type = (
        db.session.query(Sensor.S_Type)
        .filter(Sensor.id == data["Sensor"])
        .scalar()
    )
    # build a list of readings for posting

    d = {}
    l = []
    locData = {}
    tloc = ""
    if data["Controller"] == "300" or data["Controller"] == "301":
        tloc = data["Location"]
    else:
        query = db.session.query(Controller).filter(
            Controller.id == data["Controller"]
        )
 
        q = query.one()
        tloc = q.Loc_Id

    locData["location"] = tloc

    if sensor_type in (20, 40):  # oxygen, Salinity
        dv = data["value"]
        for x in dv:
            d = {}
            d["Controller"] = data["Controller"]
            d["Sensor"] = data["Sensor"]
            d["ReadingTime"] = data["ReadingTime"]
            d["SensorOption"] = x
            d["value"] = dv[x]
            if sensor_type == 20:
                if x == 'MG':
                    locData["oxygen"] = dv[x]
            else:
                if x == 'S':
                    locData["salinity"] = dv[x]
            if not (x == "default"):
                l.append(d)

    else:
        d["Controller"] = data["Controller"]
        d["Sensor"] = data["Sensor"]
        d["ReadingTime"] = data["ReadingTime"]
        d["SensorOption"] = (
            "C" if sensor_type == 10 else "US" if sensor_type == 50 else ""
        )
        d["value"] = data["value"][0]
        if sensor_type == 10:
            locData["temp"] = data["value"][0]
        elif sensor_type == 50:
            locData["water"] = data["value"][0]
        l.append(d)

    # now post the readings to db
    ctr = 0
    for rdg in l:
        if not (rdg["value"] == "0"):
            reading = Reading()
            reading.from_dict(rdg)
            reading.Location = tloc
            reading.logtime = dt.now()
            db.session.add(reading)
    db.session.commit()

    locquery = db.session.query(Location).filter(Location.Location == locData["location"]).one()
    timeNow = dt.now()
    locquery.lastDate = timeNow
    for k,val in locData.items():
        if not (val == "0"):
            if k == 'oxygen':
                locquery.oxygen = val
                locquery.oxygenTime = timeNow
            if k == 'temp':
                locquery.temp = val
                locquery.tempTime = timeNow
            if k == 'water':
                locquery.water = val
                locquery.waterTime = timeNow
            if k == 'salinity':
                locquery.salinity = val
                locquery.salinityTime = timeNow
    db.session.commit()
    if sensor_type in [20, 50]:
        sendNotifications(timeNow)
    response = jsonify({"status":"done"})
    response.status_code = 201
    return response


@bp.route("/sensor_error", methods=["POST"])
def sensor_error():
    data = request.get_json() or {}
    id_val = db.session.query(func.max(ErrorLog.id)).scalar()
    log = ErrorLog()
    log.id = id_val + 1
    log.Controller = data["controller"]
    log.Sensor = data["sensor"]
    log.Description = data["error"]
    log.ErrorTime = data["time"]
    log.LogTime = dt.now()
    db.session.add(log)
    db.session.commit()
    response = jsonify({"write_status": "ok"})
    response.status_code = 200
    return response


@bp.route("/poke", methods=["GET"])
def poke():
    """used by sensor to register connectivity status
    """
    data = request.get_json()
    q = db.session.query(Controller).filter(Controller.id == data['controller']).one()
    q.LastPoke = dt.now()
    json = {
            'poke_status': 'ok',
            'InfoText': q.InfoText,
            'Controller Status': q.StatusCd,
            'Location': q.Loc_Id,
            }
    db.session.commit()

    response = jsonify(json)
    response.status_code = 200
    return response


@bp.route("/sensorstatus", methods=["POST"])
def sensorstatus():
    sensor = SensorStatus()
    sensor.Status = int(request.args.get("id"))
    sensor.Description = request.args.get("desc")
    db.session.add(sensor)
    db.session.commit()
    response = jsonify({"Added SensorStatus": request.args.get("desc")})
    response.status_code = 201
    return response


@bp.route("/controller_version", methods=["POST"])
def controller_version():
    c_id = int(request.args.get("controller"))
    version = request.args.get("version")
    cq = db.session.query(Controller).filter(Controller.id == c_id).one()
    try:
        cq.FirmwareVersion = version
        db.session.commit()
        response = jsonify({"controller ": c_id, "version": version})
        response.status_code = 200
        debuglogger.info("FW version rcvd controller {} version {}".format(c_id, version))
    except:
        response = jsonify({"controller ": c_id, "version": version})
        response.status_code = 404
    return response


@bp.route("/sensor_by_controller", methods=["GET"])
def sensor_by_controller():

    sensors = (
        db.session.query(Sensor)
        .filter(Sensor.Controller == int(request.args.get("controller")))
        .all()
    )
    data = [
        {
            "id": s.id,
            "s_type": s.S_Type,
            "description": s.Description,
            "model": s.model.Description,
            "hw_no": s.SerialNo,
        }
        for s in sensors
    ]
    response = jsonify(data)
    response.status_code = 200
    return response


@bp.route("/sensorinfo", methods=["GET"])
def sensorinfo():

    sensors = (
        db.session.query(Sensor)
        .filter(Sensor.StatusCd == int(request.args.get("status")))
        .all()
    )
    data = [
        {
            "id": s.id,
            "SensorType": s.S_Type,
            "Brand": s.model.Description,
            "Controller": s.Controller,
            "location": s.controller.location.Description,
            "hw_id": s.SerialNo,
            "SensorStatus": s.status.Description,
        }
        for s in sensors
    ]
    response = jsonify(data)
    response.status_code = 200
    return response


@bp.route("/sensorreadings", methods=["GET"])
def sensorreadings():
    q_readings = (
        db.session.query(Reading)
        .filter(Reading.Sensor == int(request.args.get("sensor")))
        .order_by(Reading.ReadingTime.desc())
        .limit(int(request.args.get("limit")))
        .all()
    )
    json = []
    readings = [
        {
            "rec_no": r.id,
            "sensor": r.Sensor,
            "controller": r.Controller,
            "location": r.Location,
            "sensor_option": r.SensorOption,
            "reading": r.value,
            "reading_time": r.ReadingTime.strftime("%y%m%d %H:%M"),
        }
        for r in q_readings
    ]

    response = jsonify(readings)
    response.status_code = 200
    return response


@bp.route("/controller_config/<string:ctl_id>", methods=["GET"])
def get_ctlcfg():
    """returns controller configuration data for ctl_id
    """
    pass


@bp.route("/tankdetail", defaults={"path": "L01T01"})
@bp.route("/tankdetail/<path:path>")
@gzipped
def tankdetail(path):
    """Return a JSON with the pivoted readings by sensor type.
    The default period is last 24 hours.

    Parameters
    ----------
    path : string
        Location id.

    Notes
    -----
    nil.
    """

    # ctrl = db.session.query(Controller.id).filter(Controller.Loc_Id == path).all()
    hr_rdgs = (
        db.session.query(LocHourlyReading)
        .filter(LocHourlyReading.Location == path)
        .order_by(LocHourlyReading.rdate.desc(), LocHourlyReading.rhour.desc())
        .limit(100)
        .all()
    )
    json = jsonify(
        [
            {
                "Controller": r.Controller,
                "Location": path,
                "Day": r.rdate,
                "Time": str(r.rhour) + ":00",
                "DOmg": str(r.DO_MG)[:5],
                "DOPS": get_round(r.DO_PS, 1),
                "Salinity": get_round(r.EC_S, 1),
                "Conductivity": "0" if r.EC_EC is None else str(int(r.EC_EC)),
                "Temp": get_round(r.T_C, 1),
                "WaterLevel": get_round(r.WL_US, 0),
            }
            for r in hr_rdgs
        ]
    )
    response = json
    response.status_code = 200
    return response


@bp.route("/sector_pivot", defaults={"path": 1})
@bp.route("/sector_pivot/<path:path>")
@gzipped
def sector_pivot(path):
    """Return a JSON with the pivoted readings by sensor type.
    The default period is last 24 hours.

    Parameters
    ----------
    path : string
        Location id.

    Notes
    -----
    nil.
    """
    json = []
    locs = (
        db.session.query(LocHourlyReading.Sector, LocHourlyReading.Location)
        .group_by(LocHourlyReading.Sector, LocHourlyReading.Location)
        .having(LocHourlyReading.Sector == path)
        .all()
    )

    for l in locs:
        rc = (
            db.session.query(LocHourlyReading)
            .filter(LocHourlyReading.Location == l.Location)
            .order_by(
                LocHourlyReading.rdate.desc(), LocHourlyReading.rhour.desc()
            )
            .limit(1)
        )
        rc.all()
        for r in rc:
            json.append(
                {
                    "Sector": r.Sector,
                    "Location": r.Location,
                    "Controller": r.Controller,
                    "Day": str(r.rdate),
                    "Time": str(r.rhour) + ":00",
                    "DOmg": str(r.DO_MG)[:5],
                    "DOPS": get_round(r.DO_PS, 0),
                    "Salinity": get_round(r.EC_S, 1),
                    "Conductivity": "0"
                    if r.EC_EC is None
                    else str(int(r.EC_EC)),
                    "Temp": str(r.T_C)[:5],
                    "WaterLevel": get_round(r.WL_US, 0),
                }
            )
    response = jsonify(json)
    response.status_code = 200
    return response


@bp.route("/paramstatus", defaults={"path": "L01T01"})
@bp.route("/paramstatus/<path:path>")
@gzipped
def paramstatus(path):
    """Return a JSON with location current status info.
    

    Parameters
    ----------
    path : string
        Location id.

    Notes
    -----
    nil.
    """
    lastreadings = {}
    q = db.session.query(Location).filter(Location.Location == path).one()

    lastreadings["LocStat"] = "Undefined" if not q else q.status.Description
    q = db.session.query(Controller).filter(Controller.Loc_Id == path).all()
    lastreadings["CtrlStat"] = "Off"
    for c in q:
        if c.StatusCd == 2:
            lastreadings[
                "CtrlStat"
            ] = "On"  # at least one controller is active
            break
    q = (
        db.session.query(Reading)
        .filter(Reading.Location == path)
        .order_by(Reading.ReadingTime.desc())
        .all()
    )
    for c in q:
        if c.sensor.S_Type == 10:
            if not ("Temp" in lastreadings):

                lastreadings["Temp"] = val_dict(c.ReadingTime, c.value)
        if c.sensor.S_Type == 20:
            if c.SensorOption == "MG":
                if not ("DOMG" in lastreadings):
                    lastreadings["DOMG"] = val_dict(c.ReadingTime, c.value)
            elif c.SensorOption == "PS":
                if not ("DOPS" in lastreadings):
                    lastreadings["DOPS"] = val_dict(c.ReadingTime, c.value)
        if c.sensor.S_Type == 30:
            if not ("pH" in lastreadings):
                lastreadings["pH"] = val_dict(c.ReadingTime, c.value)
        if c.sensor.S_Type == 40:
            if c.SensorOption == "EC":
                if not ("ECEC" in lastreadings):
                    lastreadings["ECEC"] = val_dict(c.ReadingTime, c.value)
            elif c.SensorOption == "S":
                if not ("ECS" in lastreadings):
                    lastreadings["ECS"] = val_dict(c.ReadingTime, c.value)
        if c.sensor.S_Type in (50, 55):
            if not ("WL" in lastreadings):
                lastreadings["WL"] = val_dict(c.ReadingTime, c.value)
        if lastr_done(lastreadings):
            break
    lastrd = lastr_fill(lastreadings)

    lr = []
    lr.append(lastrd)
    json = jsonify(lr)
    response = json
    response.status_code = 200
    return response


def lastr_done(lastrds):
    sopts = ["DOMG", "DOPS", "Temp", "ECEC", "ECS", "WL"]
    for k, v in lastrds.items():
        if k in sopts:
            sopts.remove(k)
    return len(sopts) < 1


def lastr_fill(lastrds):
    sopts = ["DOMG", "DOPS", "Temp", "ECEC", "ECS", "WL"]
    for k, v in lastrds.items():
        if k in sopts:
            sopts.remove(k)
    for i in sopts:
        lastrds[i] = {"date": "", "reading": ""}
    return lastrds


def val_dict(dt, val):
    return {"date": dt.strftime("%Y-%m-%d %H:%M"), "reading": val}


@bp.route("/locsummbytype", defaults={"path": "L01T03"})
@bp.route("/locsummbytype/<path:path>")
@gzipped
def locsummbytype(path):
    """Return a JSON with the pivoted readings by sensor type.
    The default period is last 24 hours.

    Parameters
    ----------
    path : string
        Location id.

    Notes
    -----
    nil.
    """

    q = (
        db.session.query(LocSummByType)
        .filter(LocSummByType.Location == path)
        .all()
    )
    json = jsonify(
        [
            {
                "Sensor": r.Sensor,
                "SensorType": r.SensorType,
                "SensorOption": r.SensorOption,
                "Readings": r.Readings,
                "Location": r.Location,
                "Minr": r.Minr,
                "Maxr": r.Maxr,
                "Avgr": str(r.Avgr)[:5],
            }
            for r in q
        ]
    )
    response = json
    response.status_code = 200
    return response


@bp.route("/sectorsummbytype", defaults={"path": "1"})
@bp.route("/sectorsummbytype/<path:path>")
@gzipped
def sectorsummbytype(path):
    q = (
        db.session.query(
            SectorSummByType.Sector,
            SectorSummByType.SensorType,
            SectorSummByType.SensorOption,
            SectorSummByType.Readings.label("Readings"),
            SectorSummByType.Minr.label("Minr"),
            SectorSummByType.Maxr.label("Maxr"),
            SectorSummByType.Avgr.label("Avgr"),
        )
        .filter(SectorSummByType.Sector == int(path))
        .all()
    )
    json = jsonify(
        [
            {
                "Sector": r[0],
                "SensorType": r[1],
                "SensorOption": r[2],
                "Readings": r[3],
                "Minr": r[4],
                "Maxr": r[5],
                "Avgr": str(r[6])[:5],
            }
            for r in q
        ]
    )
    response = json
    response.status_code = 200
    return response


@bp.route("/locationstatus", defaults={"path": "all"})
@bp.route("/locationstatus/<path:path>")
@gzipped
def locationstatus(path):
    """ provides number of locations per location status
    default grouping is all locations.
    options : path = <sector code>|"all"
    """

    qry = (
        db.session.query(
            Location.Sector,
            Location.Loc_status,
            func.count(Location.Location).label("Count"),
        )
        .filter(Location.Location != "IT", Location.Location != "TEST")
        .group_by(Location.Sector, Location.Loc_status)
    )
    if path == "all":
        q = qry.all()
        qtot = (
            db.session.query(func.count(Location.Location))
            .filter(Location.Location != "IT", Location.Location != "TEST")
            .scalar()
        )
        qauto = (
            db.session.query(func.count(Location.Location))
            .filter(
                Location.Location != "IT",
                Location.Location != "TEST",
                Location.Automated == True,
            )
            .scalar()
        )
        qctr1 = (
            db.session.query(Location)
            .filter(Location.Location != "IT", Location.Location != "TEST")
            .all()
        )
    else:
        q = qry.having(Location.Sector == path).all()
        qtot = (
            db.session.query(func.count(Location.Location))
            .filter(
                Location.Sector == path,
                Location.Location != "IT",
                Location.Location != "TEST",
            )
            .scalar()
        )
        qauto = (
            db.session.query(func.count(Location.Location))
            .filter(
                Location.Sector == path,
                Location.Automated == True,
                Location.Location != "IT",
                Location.Location != "TEST",
            )
            .scalar()
        )

    lstat = db.session.query(LocStatus.LocStatus, LocStatus.Description).all()
    status_codes = {}
    for ls in lstat:
        status_codes[ls.LocStatus] = ls.Description
    d = {"total": qtot, "automated": qauto}
    for sc in range(1, 5):
        d[status_codes[sc].lower().replace(" ", "_")] = 0
    for r in q:
        d[status_codes[r[1]].lower().replace(" ", "_")] = r[2]
    l = [d]
    json = jsonify(l)
    response = json
    response.status_code = 200
    return json


@bp.route("/testreadings", defaults={"path": "1"})
@bp.route("/testreadings/<path:path>")
@gzipped
def testreadings(path):

    q = (
        db.session.query(
            Reading.Controller,
            Reading.Sensor,
            Reading.SensorOption,
            func.sum(Reading.value).label("TotVal"),
            func.count(Reading.value).label("cnt"),
        )
        .group_by(
            Reading.Controller,
            Reading.Sensor,
            Reading.SensorOption,
            #        ).having(LocSummByType.Sector == int(path)
        )
        .all()
    )
    json = jsonify(
        [
            {
                "Controller": r[0],
                "Sensor": r[1],
                "SensorOption": r[2],
                "Tot": r[3],
                "Cnt": r[4],
            }
            for r in q
        ]
    )
    response = json
    response.status_code = 200
    return response


@bp.route("/helpers", defaults={"path": "sectors"})
@bp.route("/helpers/<path:path>")
def helpers(path):
    json = []
    if path == "sectors":
        qr = db.session.query(Sector).all()
        for s in qr:
            json.append({"id": s.id, "Name": s.name, "Desc": s.description})
    if path == "locations":
        qr = (
            db.session.query(Location)
            .filter(Location.Sector == request.args["sector"])
            .all()
        )
        for s in qr:
            json.append({"id": s.Location, "desc": s.Description})
    elif path == "SectorOfLocation":
        qsector = (
            db.session.query(Location.Sector)
            .filter(Location.Location == request.args["location"])
            .scalar()
        )
        json.append({"sector": qsector})

    elif path == "sensortypes":
        qr = db.session.query(SensorType).all()
        for s in qr:
            json.append({"id": s.SensorType, "desc": s.Description})
    elif path == "sensorbytype":
        qr = (
            db.session.query(Sensor)
            .filter(
                Sensor.S_Type == request.args["sensortype"],
                Sensor.Controller == 1,
                Sensor.id < 2000,
            )
            .all()
        )
        for s in qr:
            json.append({"id": s.id, "desc": s.Description})

    response = jsonify(json)
    response.status_code = 200
    return response


@bp.route("/db_sectors", methods=["GET", "POST"])
@gzipped
def db_sectors():

    if request.method == "GET":
        sector_name = request.args.get("sector")
        p = db.session.query(Sector.name, Sector.description)
        if sector_name:  # date for sector named sector_name is required
            q = p.filter(Sector.name == sector_name).one()
        else:
            q = p.all()
    elif request.method == "POST":  # update data
        data = request.get_json() or {}
        if data["action"] == ACTION_ADD:
            sector = Sector()
            sector.name = data["sector_name"]
            sector.description = data["sector_description"]
            db.session.add(sector)
            db.session.commit()
            response = jsonify({})

    json = jsonify(
        [
            {
                "Sector": r[0],
                "SensorType": r[1],
                "SensorOption": r[2],
                "Readings": r[3],
                "Minr": r[4],
                "Maxr": r[5],
                "Avgr": str(r[6])[:5],
            }
            for r in q
        ]
    )
    response = json
    response.status_code = 200
    return response


@bp.route("/controller_sensors/<path:path>")
def controller_sensors(path):
    lst = []
    try:
        q = db.session.query(Location).filter(Location.Location == path).one()
        for c in q.controllers:
            for s in c.sensors:
                lst.append(
                    {
                        "controller": c.id,
                        "sensor_type": s.S_Type,
                        "sensor": s.id,
                        "info": s.SerialNo,
                        "brand": s.BrandModel,
                    }
                )
    except:
        pass
    response = jsonify(lst)
    return response


@bp.route("/linksensor/<path:path>")
def linksensor(path):
    try:
        sensor = (
            db.session.query(Sensor)
            .filter(Sensor.id == request.args["sensor"])
            .one()
        )
        sensor.Controller = path
        db.session.commit()
        message = [{"message": "Link successful"}]
        response = jsonify(message)
        response.status_code = 202  # accepted
    except:
        message = [{"message": "failed! probably sensor record missing"}]
        response = jsonify(message)
        response.status_code = 400  # accepted
    return response


@bp.route("/removesensor")
def removesensor():
    try:
        sensor = (
            db.session.query(Sensor)
            .filter(Sensor.id == request.args["sensor"])
            .one()
        )
        sensor.Controller = 1
        db.session.commit()
        message = [{"message": "De-Link successful"}]
        response = jsonify(message)
        response.status_code = 202  # accepted
    except:
        message = [{"message": "failed! probably sensor record missing"}]
        response = jsonify(message)
        response.status_code = 400  # accepted
    return response




@bp.route("/sensor_readings_report")
def sensor_readings_report():
    response = jsonify("Sensor Readings Report is still WIP")
    response.status_code = 201
    return response


@bp.route("/tank_readings_report", defaults={"path": "L01T01"})
@bp.route("/tank_readings_report/<path:path>")
@gzipped
def tank_readings_report(path):
    """Return a JSON with the pivoted readings by sensor type.
    The default period is last 24 hours.

    Parameters
    ----------
    path : string
        Location id.

    Notes
    -----
    nil.
    """

    # ctrl = db.session.query(Controller.id).filter(Controller.Loc_Id == path).all()
    hr_rdgs = (
        db.session.query(LocHourlyReading)
        .filter(LocHourlyReading.Location == path)
        .order_by(LocHourlyReading.rdate.desc(), LocHourlyReading.rhour.desc())
        .all()
    )
    outP = {
        "data": [
            {
                "Controller": r.Controller,
                "Location": path,
                "Day": r.rdate.strftime("%d-%m-%Y"),
                "Time": str(r.rhour) + ":00",
                "DOmg": get_round(r.DO_MG, 1),
                "DOPS": get_round(r.DO_PS, 1),
                "Salinity": get_round(r.EC_S, 1),
                "Conductivity": "0" if r.EC_EC is None else str(int(r.EC_EC)),
                "Temp": get_round(r.T_C, 1),
                "WaterLvl": get_round(r.WL_US, 0),
            }
            for r in hr_rdgs
        ]
    }
    outP["table"] = [
        *get_table_parameters(
            [
                "Controller",
                "Day",
                "Time",
                "DOmg",
                "DOPS",
                "Salinity",
                "Conductivity",
                "Temp",
                "WaterLvl",
            ]
        )
    ]

    json = jsonify(outP)
    response = json
    response.status_code = 200
    return response


@bp.route("/readings_by_sensor", methods=["GET"])
def readings_by_sensor():

    selection = request.args["selection"].split("*")
    dtr = lambda dt: dt[2] + "-" + dt[1] + "-" + dt[0]
    datef = dtr(selection[2].split("-"))
    datet = dtr(selection[3].split("-"))

    q_readings = (
        db.session.query(Reading)
        .filter(
            Reading.Sensor == int(selection[6]),
            Reading.Controller.between(int(selection[4]), int(selection[5])),
            Reading.Location.between(selection[0], selection[1]),
            Reading.ReadingTime.between(datef, datet),
        )
        .order_by(Reading.ReadingTime)
        .all()
    )
    json = []
    readings = {
        "data": [
            {
                "rec_no": r.id,
                "Sensor": r.Sensor,
                "Controller": r.Controller,
                "Location": r.Location,
                "Option": r.SensorOption,
                "Value": r.value,
                "Time": r.ReadingTime.strftime("%y%m%d %H:%M"),
            }
            for r in q_readings
        ]
    }
    readings["table"] = [
        *get_table_parameters(
            [
                "rec_no",
                "Sensor",
                "Controller",
                "Location",
                "Option",
                "Value",
                "Time",
            ]
        )
    ]

    response = jsonify(readings)
    response.status_code = 200
    return response


@bp.route("/trr")
@gzipped
def trr():
    """Return a JSON with the pivoted readings by sensor type.
    The default period is last 24 hours.

    Arguments:
    ----------
    arg : selection
        list of selections as :
            tank from, tank to: range of tank (location) id's to include in report
            date from, date to: period to include
            data option: auto|manual|both.
    """

    selection = request.args["selection"].split("*")
    dtr = lambda dt: dt[2] + "-" + dt[1] + "-" + dt[0]
    datef = dtr(selection[2].split("-"))
    datet = dtr(selection[3].split("-"))

    # ctrl = db.session.query(Controller.id).filter(Controller.Loc_Id == path).all()
    hr_rdgs = db.session.query(LocHourlyReading).filter(
        LocHourlyReading.Location.between(selection[0], selection[1]),
        LocHourlyReading.rdate.between(datef, datet),
    )
    if selection[4] == "manual":
        hr = hr_rdgs.filter(LocHourlyReading.Controller == 300)
    elif selection[4] == "auto":
        hr = hr_rdgs.filter(LocHourlyReading.Controller != 300)
    else:
        hr = hr_rdgs
    hr = hr.order_by(
        LocHourlyReading.rdate.desc(), LocHourlyReading.rhour.desc()
    ).all()
    outP = {
        "data": [
            {
                "Controller": r.Controller,
                "Location": r.Location,
                "Day": r.rdate.strftime("%d-%m-%Y"),
                "Time": str(r.rhour) + ":00",
                "DOmg": get_round(r.DO_MG, 1),
                "DOPS": get_round(r.DO_PS, 1),
                "Salinity": get_round(r.EC_S, 1),
                "Conductivity": "0" if r.EC_EC is None else str(int(r.EC_EC)),
                "Temp": get_round(r.T_C, 1),
                "WaterLvl": get_round(r.WL_US, 0),
            }
            for r in hr
        ]
    }
    outP["table"] = [
        *get_table_parameters(
            [
                "Day",
                "Time",
                "Location",
                "Controller",
                "DOmg",
                "DOPS",
                "Salinity",
                "Conductivity",
                "Temp",
                "WaterLvl",
            ]
        )
    ]

    json = jsonify(outP)
    response = json
    response.status_code = 200
    return response


@bp.route("/trr_exception")
@gzipped
def trr_exception():
    """Return a JSON with the pivoted readings by sensor type, 
    where readings are not within acceptable range.

    Arguments:
    ----------
    arg : selection
        list of selections as :
            tank from, tank to: range of tank (location) id's to include in report
            date from, date to: period to include
            data option: auto|manual|both.
    """
    MIN_DO = 3.0
    MAX_DO = 15.0
    MIN_Salinity = 20.0
    MAX_Salinity = 42.0
    MIN_Temp = 20.0
    MAX_Temp = 32.0

    selection = request.args["selection"].split("*")
    dtr = lambda dt: dt[2] + "-" + dt[1] + "-" + dt[0]
    datef = dtr(selection[2].split("-"))
    datet = dtr(selection[3].split("-"))

    # ctrl = db.session.query(Controller.id).filter(Controller.Loc_Id == path).all()
    hr_rdgs = db.session.query(LocHourlyReading).filter(
        LocHourlyReading.Location.between(selection[0], selection[1]),
        LocHourlyReading.rdate.between(datef, datet),
        or_(
            LocHourlyReading.DO_MG.is_(None),
            LocHourlyReading.EC_S.is_(None),
            LocHourlyReading.T_C.is_(None),
            ~LocHourlyReading.DO_MG.between(MIN_DO, MAX_DO),
            ~LocHourlyReading.EC_S.between(MIN_Salinity, MAX_Salinity),
            ~LocHourlyReading.T_C.between(MIN_Temp, MAX_Temp),
        ),
    )
    if selection[4] == "manual":
        hr = hr_rdgs.filter(LocHourlyReading.Controller == 300)
    elif selection[4] == "auto":
        hr = hr_rdgs.filter(LocHourlyReading.Controller != 300)
    else:
        hr = hr_rdgs
    hr = hr.order_by(
        LocHourlyReading.rdate.desc(), LocHourlyReading.rhour.desc()
    ).all()
    outP = {
        "data": [
            {
                "Controller": r.Controller,
                "Location": r.Location,
                "Day": r.rdate.strftime("%d-%m-%Y"),
                "Time": str(r.rhour) + ":00",
                "DOmg": get_round(r.DO_MG, 1),
                "DOPS": get_round(r.DO_PS, 1),
                "Salinity": get_round(r.EC_S, 1),
                "Conductivity": "0" if r.EC_EC is None else str(int(r.EC_EC)),
                "Temp": get_round(r.T_C, 1),
                "WaterLvl": get_round(r.WL_US, 0),
            }
            for r in hr
        ]
    }
    outP["table"] = [
        *get_table_parameters(
            [
                "Day",
                "Time",
                "Location",
                "Controller",
                "DOmg",
                "DOPS",
                "Salinity",
                "Conductivity",
                "Temp",
                "WaterLvl",
            ]
        )
    ]

    json = jsonify(outP)
    response = json
    response.status_code = 200
    return response


@bp.route("/sendMail")
def sendMail():
    subject="NWP Exception Notification"
    sender = "nwp@naqua.com.sa"
    recipients = ["nassiratik@hotmail.com"]
    text_body = "NWP Alert! Tank L01T01 Oxygen level 2.4"
    html_body = "<H1>NWP Alert</H1><p>Tank L01T01 Oxygen level 2.4</p>"
    msg = Message(subject,sender=sender,
        recipients=recipients,
        cc = ["nassiratik@naqua.com.sa"],
        bcc = ["nassiratik@gmail.com"],
        reply_to = "nassiratik@naqua.com.sa",)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    res = jsonify("mails sent")
    # res = jsonify({"mails sent": len(recipients)})
    response = res
    response.status_code  = 200
    return response

def sendNotifications(eventTime):
    if not sysOptions["sendSMSNotification"]:
        return
    messages=[]

    alerts = get_alerts(eventTime)
    for l in alerts:
        msgEvent = l["type"] + " level {}".format(l["value"]) 
        messages.append({"location": l["location"], "message": " Tank " + l["location"] + ", " + msgEvent})
    sendNotifs(eventTime, messages)

def get_alerts(eventTime):
    """prepare json with exceptions in parameter values
    """
    rtime = lambda dt: dt.strftime("%d-%m-%y %I:%M:%S")
    lst = []
    prange = db.session.query(ParamRange).filter(ParamRange.sector == 1).one()
    q = db.session.query(Location
        ).filter(Location.Loc_status == 2,
            Location.Sector == 1,
        ).all()

    for c in q:

        maxOffline = prange.maxOfflineAuto if c.Automated else prange.maxOfflineManual
        if not isOffline(c.oxygenTime, maxOffline):
            # print("time1: {}, eventTime: {}, equality {}".format(rtime(c.oxygenTime), rtime(eventTime), rtime(c.oxygenTime)==rtime(eventTime)))

            if not(prange.oxygenMin <= c.oxygen <= prange.oxygenMax) and rtime(c.oxygenTime) == rtime(eventTime):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "oxygen",
                        "value": c.oxygen,
                    }
                )
        if not isOffline(c.waterTime, maxOffline):
            if not(prange.waterMin <= c.water <= prange.waterMax) and rtime(c.oxygenTime) == rtime(eventTime):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "water",
                        "value": c.water,
                    }
                )
    # print(eventTime)
    # print(lst)
    return lst


def isOffline(lastDate, maxOffline):
    timeDiff = dt.now() - lastDate
    minDiff = timeDiff.seconds//60 if timeDiff.days == 0 else 999
    return (minDiff > maxOffline)


def sendNotifs(eventTime, messages):

    rtime = lambda dt: dt.strftime("%d-%m-%y %I:%M:%S")
    msgUnicode = 'E'
    msgSender = sysOptions["smsSender"]
    userName = sysOptions["smsUser"]
    userPW = sysOptions["smsPW"]
    URL = sysOptions["smsURL"] 
    users = db.session.query(User).filter(~(User.notification == "NONE")).all()
    for user in users:
        for message in messages:
            if not hasMsgBeenSent(message["location"], eventTime):
                if user.notification in ["SMS", "BOTH"]:
                    msgText = "NWP-PGO alert!" + message["message"]
                    payload = "?username=" + userName
                    payload += "&password=" + userPW
                    payload += "&mobile=" + user.mobile
                    payload += "&unicode=" + msgUnicode
                    payload += "&message=" + msgText + " (" + rtime(eventTime) + ")"
                    payload += "&sender=" + msgSender
                    notification = Notification()
                    notification.location = message["location"]
                    notification.eventTime = eventTime
                    notification.user = user.name
                    notification.mobile = user.mobile
                    db.session.add(notification)
                    db.session.commit()
                    response = requests.get(URL+payload, timeout=13)
                if user.notification in ["EMAIL", "BOTH"]:
                    debuglogger.info("sending notif email : %s" %(message["message"]))
                    subject="NWP Exception Notification"
                    sender = "nwp@naqua.com.sa"
                    recipients = [user.email]
                    text_body = "NWP-PGO alert!" + message["message"]
                    html_body1 = "<H1>NWP-PGO Alert</H1><p>" + message["message"] + "</p>"
                    html_body2 = """<a href='http://param.naqua.com.sa/alerts'>Click here for more information</a>
                    <p>This is an automatically generated message. Please do not reply</p>
                    <p>If you do not wish to be receiving these notifications, please contact IT Support</p>
                    """
                    msg = Message(subject,sender=sender,
                        recipients=recipients,
                        cc = [],
                        bcc = [],
                        reply_to = "no_reply@naqua.com.sa",)
                    msg.body = text_body
                    msg.html = html_body1 + html_body2
                    mail.send(msg)
    return


def hasMsgBeenSent(location, eventTime):
    rtime = lambda dt: dt.strftime("%d-%m-%y %I:%M:%S")
    notifications = db.session.query(Notification
        ).filter(Notification.location==location
        ).order_by(Notification.id.desc()
        ).all()

    for n in notifications:
        if rtime(n.eventTime) == rtime(eventTime):
            return True
        if rtime(n.eventTime) < rtime(eventTime):
            return False
    return False
