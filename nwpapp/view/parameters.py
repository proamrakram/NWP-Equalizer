"""View module for the nwp web app.

This module defines how our data is presented on the different URLs.
"""
# TODO(0): Make sure all functions are follow the snake_case pattern
import  json, requests
from datetime import datetime as dt
from flask import Blueprint, g, render_template, url_for, request, flash, jsonify
from flask import make_response
# from flask_weasyprint import HTML, render_pdf
import pdfkit
from sqlalchemy import func
# from nwpapp import app
from nwpapp.forms.forms import (
    sector_form,
    location_form,
    sensor_form,
    controller_form,
    manual_form,
    report_form_001,
    report_form_003,
    report_form_a001,
)
from nwpapp.model.model import (
    db,
    Sector,
    Location,
    LocStatus,
    Controller,
    ControllerVersion,
    ControllerStatus,
    Sensor,
    SensorType,
    Model,
    SensorStatus,
    ParamRange,
)
from nwpapp.view.auth import login_required
from . import baselogger, debuglogger

bp = Blueprint("parameters", __name__)


def set_nav_items(g):
    """Set the sidebar and top navbar structure.

    Parameters
    ----------
    g : flask.g
    """
    sectors = []
    for group in g.user.groups:
        for sector in group.sectors:
            sectors.append(sector.name)

    reports = [
        "Sensor Readings Report",
        "Tank Readings Report",
        "Exception Report",
        "Controllers Report",
    ]
    data = ["Manual Entry", "Other Entry"]

    g.nav_items = [
        {"name": "Overview", "icon": "fa-tachometer-alt"},
        {"name": "Sectors", "icon": "fa-chart-bar", "submenu": sectors},
        {"name": "Manual Data Entry", "icon": "fa-cogs", "submenu": data},
        {"name": "Reports", "icon": "fa-cogs", "submenu": reports},
        {"name": "Alerts", "icon": "fa-frown"},
        {"name": "About", "icon": "fa-info-circle"},
        {"name": "Contact", "icon": "fa-paper-plane"},
    ]
    if g.user.superuser:
        g.nav_items.append(
            {
                "name": "Backend Activities",
                "icon": "fa-cogs",
                "submenu": [
                    "manage sectors",
                    "manage locations",
                    "manage controllers",
                    "manage sensors",
                ],
            }
        )


##############################################################################
#                            Main Pages                                      #
##############################################################################
@bp.route("/")
@bp.route("/overview")
@login_required
def overview():
    """Render the nwp overview page.

    Notes
    -----
    Requires users to previously login.
    The template used is nwp/overview.html.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Overview"

    return render_template("nwp/overview.html")


@bp.route("/about")
@login_required
def about():
    """Render the About web page.

    Notes
    -----
    Requires users to previously login.
    The template used is nwp/about.html.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "About"

    return render_template("nwp/about.html")


@bp.route("/contact")
@login_required
def contact():
    """Render the Contact web page.

    Notes
    -----
    Requires users to previously login.
    The template used is nwp/contact.html.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Contact"

    return render_template("nwp/contact.html")


##############################################################################
#                          Submenu Pages                                     #
##############################################################################
@bp.route("/sector1")
@login_required
def sector1():
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Sector1"
    g.description = "Sector 1 data"
    g.json_url = url_for("api.sector_pivot", path=1)
    g.sector = 1

    return render_template("nwp/sector.html")


@bp.route("/sector2")
@login_required
def sector2():
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "sector2"
    g.description = "Sector 2 data"
    g.json_url = url_for("api.sector_pivot", path=2)
    g.sector = 2

    return render_template("nwp/sector.html")


@bp.route("/samp")
@login_required
def samp():
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "samp"
    g.description = "Supply Tanks data"
    g.json_url = url_for("api.sector_pivot", path=3)
    g.sector = 3

    return render_template("nwp/sector.html")


@bp.route("/hatchery")
@login_required
def hatchery():
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "hatchery"
    g.description = "Hatchery data"
    g.json_url = url_for("api.sector_pivot", path=4)
    g.sector = 4

    return render_template("nwp/sector.html")


@bp.route("/sensor_readings_pdf")
@login_required
def sensor_readings_pdf():
    """Generates data for sector details report (r-nnn) and renders in pdf format.

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Sector1"
    g.description = "Sector 1 data"
    g.json_url = url_for("api.sector_pivot", path=1)
    g.sector = 1

    location_summary = [
        {
            "SensorType": "20",
            "SensorOption": "MG",
            "Readings": "3",
            "Minr": "4.5",
            "Maxr": "11.2",
            "Avgr": "6.9",
        },
        {
            "SensorType": "30",
            "SensorOption": "S",
            "Readings": "4",
            "Minr": "28",
            "Maxr": "42",
            "Avgr": "41",
        },
    ]

    location_data = [
        {
            "Location": "L02T01",
            "Day": "13-01-2019",
            "Time": "14:00",
            "DOmg": "7.5",
            "DOPS": "125",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
        {
            "Location": "L02T02",
            "Day": "13-01-2019",
            "Time": "15:00",
            "DOmg": "7.4",
            "DOPS": "120",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
        {
            "Location": "L02T03",
            "Day": "13-01-2019",
            "Time": "16:00",
            "DOmg": "7.3",
            "DOPS": "121",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
    ]

    html_out = render_template(
        "nwp/rep_sector.html", location_data=location_data, location_summary=location_summary
    )

    return render_pdf(HTML(string=html_out))


@bp.route("/sensor_readings_pdfkit")
@login_required
def sensor_readings_pdfkit():
    """Generates data for sector details report (r-nnn) and renders in pdf format.

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Sector1"
    g.description = "Sector 1 pdfkit"
    g.json_url = url_for("api.sector_pivot", path=1)
    g.sector = 1

    location_summary = [
        {
            "SensorType": "20",
            "SensorOption": "MG",
            "Readings": "3",
            "Minr": "4.5",
            "Maxr": "11.2",
            "Avgr": "6.9",
        },
        {
            "SensorType": "30",
            "SensorOption": "S",
            "Readings": "4",
            "Minr": "28",
            "Maxr": "42",
            "Avgr": "41",
        },
    ]

    location_data = [
        {
            "Location": "L01T01",
            "Day": "13-01-2019",
            "Time": "14:00",
            "DOmg": "7.5",
            "DOPS": "125",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
        {
            "Location": "L01T02",
            "Day": "13-01-2019",
            "Time": "15:00",
            "DOmg": "7.4",
            "DOPS": "120",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
        {
            "Location": "L01T03",
            "Day": "13-01-2019",
            "Time": "16:00",
            "DOmg": "7.3",
            "DOPS": "121",
            "Salinity": "39.8",
            "Conductivity": "41520",
            "Temp": "30.25",
            "WaterLevel": "133",
        },
    ]

    html_out = render_template(
        "nwp/rep_sector.html", location_data=location_data, location_summary=location_summary
    )
    pdfout = pdfkit.from_string(html_out, False)
    response = make_response(pdfout)
    response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Desposition'] = 'inline; filename=%s.pdf' % 'readings.pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.pdf' % 'readings.pdf'
    return response


@bp.route("/controllers_report", methods=["GET", "POST"])
@login_required
def controllers_report():
    """Load form report parameters, and generates Tank Readings Report(id002)
    with reading that are outside acceptable range

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Controllers List"
    g.report = g.page
    g.description = g.page
    g.report_id = "a001"
    form = report_form_a001()
    if request.method == "POST":
        if not form.validate():
            flash("invalid info entered!")

            return render_template(
                "nwp/form_report_a001.html", form=form, result="error"
            )

        controllers = controller_list()
        return render_template("nwp/rep_a001.html", controllers=controllers)

    return render_template("nwp/form_report_a001.html", form=form)


@bp.route("/sensor_readings_report", methods=["GET", "POST"])
@login_required
def sensor_readings_report():
    """Load form report parameters, and generates Tank Readings Report(id001)

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Sensor Readings"
    g.report = g.page
    g.description = g.page
    g.report_id = "003"
    form = report_form_003()
    if request.method == "POST":

        if not form.validate():
            flash("invalid info entered!")

            return render_template(
                "nwp/form_report_001.html", form=form, result="error"
            )

        selection = [
            form.location_from.data,
            form.location_to.data,
            form.date_from.data,
            form.date_to.data,
            str(form.controller_from.data),
            str(form.controller_to.data),
            str(form.sensor_id.data),
        ]
        g.json_url = url_for(
            "api.readings_by_sensor", selection="*".join(selection)
        )

        return render_template("nwp/report_tabulator.html", selection=selection)

    return render_template("nwp/form_report_003.html", form=form)


@bp.route("/tank_readings_report", methods=["GET", "POST"])
@login_required
def tank_readings_report():
    """Load form report parameters, and generates Tank Readings Report(id001)

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Tank Readings Report"
    g.report = g.page
    g.description = g.page
    g.report_id = "001"
    form = report_form_001()
    form.sector.choices = db_masters("sector")
    form.location_from.choices = db_masters("location")
    form.location_to.choices = db_masters("location")
    if request.method == "POST":

        if not form.validate():
            flash("invalid info entered!")

            return render_template(
                "nwp/form_report_001.html", form=form, result="error"
            )

        selection = [
            form.location_from.data,
            form.location_to.data,
            form.date_from.data,
            form.date_to.data,
            form.data_option.data,
        ]
        g.json_url = url_for("api.trr", selection="*".join(selection))

        return render_template("nwp/report_tabulator.html", selection=selection)

    return render_template("nwp/form_report_001.html", form=form)


@bp.route("/exception_report", methods=["GET", "POST"])
@login_required
def exception_report():
    """Load form report parameters, and generates Tank Readings Report(id002)
    with reading that are outside acceptable range

    Notes
    -----
    Requires users to previously login.
    """
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Exception Report"
    g.report = g.page
    g.description = g.page
    g.report_id = "002"
    form = report_form_001()
    form.sector.choices = db_masters("sector")
    form.location_from.choices = db_masters("location")
    form.location_to.choices = db_masters("location")
    if request.method == "POST":

        if not form.validate():
            flash("invalid info entered!")

            return render_template(
                "nwp/form_report_001.html", form=form, result="error"
            )

        selection = [
            form.location_from.data,
            form.location_to.data,
            form.date_from.data,
            form.date_to.data,
            form.data_option.data,
        ]
        g.json_url = url_for("api.trr_exception", selection="*".join(selection))

        return render_template("nwp/report_tabulator.html", selection=selection)

    return render_template("nwp/form_report_001.html", form=form)


@bp.route("/location_parameters/<location>")
@login_required
def location_parameters(location):
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "Location Parameters"
    g.location = location
    g.description = "Tank Detailed Parameters"
    g.json_url = url_for("api.tankdetail", path=location)

    return render_template("nwp/locdetail.html")

# TODO(2): Start the next refactoring from here to bottom. All of the above are done! it's line 441
@bp.route("/manage_sectors", methods=["POST", "GET"])
@login_required
def manage_sectors():
    set_nav_items(g)
    g.page = "manage sectors"
    g.description = "Manage Sectors"
    form = sector_form()
    if request.method == "POST":
        if form.submit_button.data:
            if form.validate() is False:
                flash("All fields must be entered")
                return render_template(
                    "nwp/form_manage_sectors.html",
                    form=form,
                    result="error",
                    sectors=db_sectors(),
                )
            else:
                db_sectors(
                    "add",
                    [form.sector_name.data, form.sector_description.data],
                )

        elif form.delete_button.data:
            db_sectors("del", form.sector_name.data)

        else:
            flash("Request not determined")

        return render_template(
            "nwp/form_manage_sectors.html",
            form=form,
            result="ok",
            sectors=db_sectors(),
        )
    elif request.method == "GET":
        return render_template(
            "nwp/form_manage_sectors.html",
            form=form,
            result="entry",
            sectors=db_sectors(),
        )


@bp.route("/manage_locations", methods=["POST", "GET"])
@login_required
def manage_locations():
    """add, update, delete locations.

    Notes
    -----
    Requires users to previously login.
    """
    RES_OK = "ok"
    RES_FAIL = "fail"
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "manage locations"
    g.description = "Manage Locations"
    form = location_form()
    form.sector.choices = db_sectors("get_tuples")
    form.status.choices = db_masters("loc_status")
    result = ""
    if request.method == "POST":
        if form.submit_button.data:
            if form.validate() is False:
                flash("Important data is invalid/missing!")
                return render_template(
                    "nwp/form_manage_locations.html",
                    form=form,
                    result="error",
                    locations=db_locations(),
                )
            else:
                lst = [
                    form.location_id.data,
                    form.location_description.data,
                    form.status.data,
                    form.sector.data,
                    form.specs.data,
                ]
                db_locations("add", lst)
                result = RES_OK
        elif form.delete_button.data:
            try:
                db_locations("del", form.location_id.data)
                result = RES_OK
            except:
                flash(
                    "Cannot delete location "
                    + form.location_id.data
                    + ". Child records exist"
                )
                result = RES_FAIL
        else:
            flash("Request not determined")
        return render_template(
            "nwp/form_manage_locations.html",
            form=form,
            result=result,
            locations=db_locations(),
        )
    elif request.method == "GET":
        return render_template(
            "nwp/form_manage_locations.html",
            form=form,
            result=result,
            locations=db_locations(),
        )


@bp.route("/manage_sensors", methods=["POST", "GET"])
@login_required
def manage_sensors():
    """add, update, delete locations.

    Notes
    -----
    Requires users to previously login.
    """
    RES_OK = "ok"
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "manage sensors"
    g.description = "Manage Sensors"
    form = sensor_form()
    form.s_type.choices = db_masters("s_type")
    form.status.choices = db_masters("loc_status")
    form.model.choices = db_masters("model")
    result = ""
    if request.method == "POST":
        if form.submit_button.data:
            if form.validate() == False:
                flash("Important data is invalid/missing!")
                return render_template(
                    "nwp/form_manage_sensors.html",
                    form=form,
                    result="error",
                    sensors=db_sensors(),
                )
            else:
                lst = [
                    form.s_id.data,
                    form.s_type.data,
                    form.s_description.data,
                    form.model.data,
                    form.status.data,
                    form.serial_no.data,
                ]
                result = db_sensors("add", lst)
                if result != RES_OK:
                    flash("Failed. " + result)
                    return render_template(
                        "nwp/form_manage_sensors.html",
                        form=form,
                        result="error",
                        sensors=db_sensors(),
                    )
        elif form.delete_button.data:
            result = db_sensors("del", form.s_id.data)
            if result != RES_OK:
                flash("Failed. " + result)
        else:
            flash("Request not determined")
        return render_template(
            "nwp/form_manage_sensors.html",
            form=form,
            result=result,
            sensors=db_sensors(),
        )
    elif request.method == "GET":
        return render_template(
            "nwp/form_manage_sensors.html",
            form=form,
            result=result,
            sensors=db_sensors(),
        )


@bp.route("/manage_controllers", methods=["POST", "GET"])
@login_required
def manage_controllers():
    """add, update, delete controllers.

    Notes
    -----
    Requires users to previously login.
    """
    RES_OK = "ok"
    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "manage controllers"
    g.description = "Manage Controllers"
    form = controller_form()
    form.version.choices = db_masters("version")
    form.cstatus.choices = db_masters("controller_status")
    form.csector.choices = db_masters("sector")
    form.clocation.choices = db_masters("location")
    result = ""
    if request.method == "POST":
        if form.submit_button.data:
            if form.validate() == False:
                flash("Important data is invalid/missing!")
                return render_template(
                    "nwp/form_manage_controllers.html",
                    form=form,
                    result="error",
                    controllers=db_controllers(),
                )
            else:
                lst = [
                    form.c_id.data,
                    form.version.data,
                    form.clocation.data,
                    form.date_manuf.data,
                    form.specs.data,
                    form.cstatus.data,
                ]
                result = db_controllers("add", lst)
                if result != RES_OK:
                    flash("Failed. " + result)
                    return render_template(
                        "nwp/form_manage_controllers.html",
                        form=form,
                        result="error",
                        controllers=db_controllers(),
                    )
        elif form.delete_button.data:
            result = db_controllers("del", form.c_id.data)
            if result != RES_OK:
                flash("Failed. " + result)
        else:
            flash("Request not determined")
        return render_template(
            "nwp/form_manage_controllers.html",
            form=form,
            result=result,
            controllers=db_controllers(),
        )
    elif request.method == "GET":
        return render_template(
            "nwp/form_manage_controllers.html",
            form=form,
            result=result,
            controllers=db_controllers(),
        )


@bp.route("/manual_entry", methods=["GET"])
@login_required
def manual_entry():
    """Add manual readings to database
    no POST for this form, as readings are uploaded via AJAX

    Notes
    -----
    Requires users to previously login.
    """

    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "manual entry"
    g.description = "Manual Entry"
    form = manual_form()
    form.sector.choices = db_masters("sector")
    form.location.choices = db_masters("location", 3)
    form.unit.choices = db_masters("manual_units")
    form.reading_hour.choices = [("1", "1:001m TO 2:00am")]
    # print(f"Secret Key: {app.config['SECRET_KEY']}")
    return render_template("nwp/form_manual_entry.html", form=form)


@bp.route("/other_entry", methods=["GET"])
@login_required
def other_entry():
    """Add manual readings to database
    no POST for this form, as readings are uploaded via AJAX

    Notes
    -----
    Requires users to previously login.
    """

    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "other entry"
    g.description = "Other Entry"
    form = manual_form()
    form.sector.choices = db_masters("sector")
    form.location.choices = db_masters("location", 3)
    form.unit.choices = db_masters("manual_units")
    form.reading_hour.choices = [("1", "1:001m TO 2:00am")]
    return render_template("nwp/form_manual_entry.html", form=form)


@bp.route("/alerts", methods=["GET"])
@login_required
def alerts():
    """shows exceptions in water parameter readings
    Notes
    -----
    Requires users to previously login.
    """

    if "nav_items" not in g:
        set_nav_items(g)
    g.page = "alerts"
    g.description = "exceptions"
    alerts_json = get_alerts()
    # response = requests.get("http://localhost:5000" + url_for("api.alerts"))
    # alerts_json = json.loads(response.text)
    return render_template("nwp/alerts.html", alerts_json = alerts_json)


@bp.route("/hr_basic_info/<string:emp_id>", methods=["GET"])
def hr_basic_info(emp_id):
    """temp route to work with CashDesk for hr data. This should be implemented in the Naqua API
    """
    json = {'emp_id': emp_id,
              'emp_name': 'Nassir Atik',
              'emp_phone': '0555620127',
              'emp_email': 'nassiratik@naqua.com.sa',
              'govt_id': '2098917350',
              'url': 'https://param.naqua.com.sa/hr_basic_data/<string:emp_cd>',
              }

    response = jsonify(json)
    response.status_code = 404
    return response


def db_locations(action="get", data=None):
    if action == "get":
        q = db.session.query(
            Location.Location,
            Location.Description,
            Location.Loc_status,
            Location.Sector,
            Location.Specs,
        ).all()

        d_locations = [
            {
                "id": r[0],
                "desc": r[1],
                "status": r[2],
                "sector": r[3],
                "specs": r[4],
            }
            for r in q
        ]
        return d_locations
    elif action == "add":
        try:
            exist = (
                db.session.query(Location)
                .filter(Location.Location == data[0])
                .one()
            )
            exist.Description = data[1]
            exist.Loc_status = data[2]
            exist.Sector = data[3]
            exist.Specs = data[4]
        except:
            location = Location()
            location.Location = data[0]
            location.Description = data[1]
            location.Loc_status = data[2]
            location.Sector = data[3]
            location.Specs = data[4]
            location.Automated = 0
            location.lastDate = dt.now()
            location.oxygen = 0
            location.temp = 0
            location.water = 0
            location.salinity = 0
            location.oxygenDate = dt.now()
            location.tempDate = dt.now()
            location.waterDate = dt.now()
            location.salinityDate = dt.now()
            db.session.add(location)
        db.session.commit()

    elif action == "del":
        location = (
            db.session.query(Location).filter(Location.Location == data).one()
        )
        db.session.delete(location)
        db.session.commit()


def db_sensors(action="get", data=None):
    if action == "get":
        q = db.session.query(Sensor).order_by(Sensor.id.desc()).all()
        d_sensors = [
            {
                "id": r.id,
                "s_type": r.S_Type,
                "desc": r.Description,
                "model": r.BrandModel,
                "status": r.StatusCd,
                "hw_no": r.SerialNo,
                "controller": r.Controller,
                "location": r.controller.Loc_Id,
            }
            for r in q
        ]
        return d_sensors
    elif action == "add":
        try:
            exist = (
                db.session.query(Sensor).filter(Sensor.id == int(data[0])).one()
            )
            exist.S_Type = data[1]
            exist.Description = data[2]
            exist.BrandModel = data[3]
            exist.StatusCd = data[4]
            exist.SerialNo = data[5]
        except:
            sensor = Sensor()
            sensor.S_Type = data[1]
            sensor.Description = data[2]
            sensor.BrandModel = data[3]
            sensor.StatusCd = data[4]
            sensor.SerialNo = data[5]
            # standard controller no. for IT Test Controller = 1
            sensor.Controller = 1
            db.session.add(sensor)
        db.session.commit()
        return "ok"
    elif action == "del":
        sensor = db.session.query(Sensor).filter(Sensor.id == data).one()
        if len(sensor.readings) > 0:
            return (
                "Cannot delete, "
                + str(len(sensor.readings))
                + " readings found!"
            )
        else:
            db.session.delete(sensor)
            db.session.commit()
            return "ok"


def db_controllers(action="get", data=None):
    if action == "get":
        q = db.session.query(Controller).order_by(Controller.id.desc()).all()
        d_controllers = [
            {
                "id": r.id,
                "version": r.Version,
                "location": r.Loc_Id,
                "date_manuf": r.DateManuf.strftime("%Y-%m-%d"),
                "description": r.InfoText,
                "status": r.StatusCd,
                "sector": r.location.Sector,
                "fwversion": r.FirmwareVersion,
            }
            for r in q
        ]
        return d_controllers
    elif action == "add":
        old_loc = ""
        try:
            exist = (
                db.session.query(Controller)
                .filter(Controller.id == data[0])
                .one()
            )
            old_loc = exist.Loc_Id
            exist.Version = data[1]
            exist.Loc_Id = data[2]
            exist.DateManuf = data[3]
            exist.InfoText = data[4]
            exist.StatusCd = data[5]
        except:
            controller = Controller()
            controller.Version = data[1]
            controller.Loc_Id = data[2]
            controller.DateManuf = data[3]
            controller.InfoText = data[4]
            controller.StatusCd = data[5]
            db.session.add(controller)

        # if location is changed in an existing controller,or of it is new controller (loc is blank)
        # then set the Automated flag in Location
        if old_loc != data[2]:
            qloc = (
                db.session.query(Location)
                .filter(Location.Location == data[2])
                .all()
            )
            for ql in qloc:
                ql.Automated = True
            if old_loc != "":
                qloc = (
                    db.session.query(Location)
                    .filter(Location.Location == old_loc)
                    .all()
                )
                for ql in qloc:
                    ql.Automated = False

        db.session.commit()
        return "ok"
    elif action == "del":
        controller = (
            db.session.query(Controller).filter(Controller.id == data).one()
        )
        cloc = controller.Loc_Id
        if len(controller.readings) > 0:
            return (
                "Cannot delete, "
                + str(len(controller.readings))
                + " readings found!"
            )
        else:
            sensors = (
                db.session.query(Sensor).filter(Sensor.Controller == data).all()
            )
            for s in sensors:
                s.Controller = 1  # standard controller number for IT

            # if no more controllers are linked to deleted location, set Automated flag to false
            ctr_in_cloc = (
                db.session.query(func.count(Controller.id))
                .filter(Controller.Loc_Id == cloc)
                .scalar()
            )
            print("Count of controllers = " + str(ctr_in_cloc))
            if ctr_in_cloc > 0:
                qloc = (
                    db.session.query(Location)
                    .filter(Location.Location == cloc)
                    .one()
                )
                qloc.Automated = False
                print("Location " + qloc.Location + " is now not automated")

            db.session.delete(controller)

            db.session.commit()
            return "ok"


def db_sectors(action="get", data=None):
    if action == "get":
        q = db.session.query(Sector.id, Sector.name, Sector.description).all()

        d_sectors = [
            {"rec_id": r[0], "sector_name": r[1], "sector_desc": r[2]}
            for r in q
        ]
        return d_sectors
    elif action == "get_tuples":
        sectors = db.session.query(Sector).order_by(Sector.name).all()
        d_sectors = [(r.id, r.name) for r in sectors]
        return d_sectors
    elif action == "add":
        try:
            exist = db.session.query(Sector).filter(Sector.name == data[0]).one()
            exist.name = data[0]
            exist.description = data[1]
        except:
            sector = Sector()
            sector.name = data[0]
            sector.description = data[1]
            db.session.add(sector)
        db.session.commit()
    elif action == "del":
        sector = db.session.query(Sector).filter(Sector.name == data).one()
        db.session.delete(sector)
        db.session.commit()


def db_masters(action, opt=None):
    if action == "loc_status":
        q = db.session.query(LocStatus).all()
        d_out = [(r.LocStatus, r.Description) for r in q]
    elif action == "model":
        q = db.session.query(Model).all()
        d_out = [(r.BrandModel, r.Brand + "-" + r.Model) for r in q]
    elif action == "s_type":
        q = db.session.query(SensorType).all()
        d_out = [(r.SensorType, r.Description) for r in q]
    elif action == "version":
        q = db.session.query(ControllerVersion).all()
        d_out = [(r.id, r.version) for r in q]

    elif action == "controller_status":
        q = db.session.query(ControllerStatus).all()
        d_out = [(r.Status, r.Description) for r in q]
    elif action == "sector":
        q = db.session.query(Sector).all()
        d_out = [(r.id, r.name) for r in q]
    elif action == "location":
        if opt is None:
            q = db.session.query(Location).all()
        else:
            q = db.session.query(Location).filter(Location.Sector == opt).all()

        d_out = [(r.Location, r.Description) for r in q]
    elif action == "manual_units":
        # controller id's 300 and above are reserved for manual parameter reading units.
        q = db.session.query(Controller).filter(Controller.id > 299).all()
        d_out = [(r.id, r.InfoText) for r in q]

    else:
        d_out = []
    return d_out


def controller_list():
    lst = []
    q = db.session.query(
        Controller.id,
        Controller.Loc_Id,
        Controller.FirmwareVersion,
        Controller.InfoText,
        Controller.StatusCd,
    ).all()
    lst = [
        {
            "id": r[0],
            "Location": r[1],
            "Firmware": r[2],
            "Info": r[3],
            "Status": db.session.query(ControllerStatus.Description)
             .filter(ControllerStatus.Status == r[4])
             .scalar(),
        }
        for r in q
    ]

    return lst


def get_alerts():
    """prepare json with exceptions in parameter values
    """
    lst = []
    prange = db.session.query(ParamRange).filter(ParamRange.sector == 1).one()
    q = db.session.query(Location
        ).filter(Location.Loc_status == 2,
            Location.Sector == 1,
        ).all()

    for c in q:

        # timeDiff = dt.now() - c.lastDate
        # minDiff = timeDiff.seconds//60 if timeDiff.days == 0 else 999
        maxOffline = prange.maxOfflineAuto if c.Automated else prange.maxOfflineManual
        if isOffline(c.lastDate, maxOffline):
            lst.append(
                {
                    "location": c.Location,
                    "type": "offline",
                    "value": 0.0,
                    "time": c.lastDate.strftime("%d-%m-%y %I:%M%p"),
                }
            )
        else: 
            if isOffline(c.oxygenTime, maxOffline):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "oxygen",
                        "subtype": "offline",
                        "value": 0.0,
                        "time": c.oxygenTime.strftime("%d-%m-%y %I:%M%p"),
                    }
                )
            else:
                if not(prange.oxygenMin <= c.oxygen <= prange.oxygenMax) and not(c.oxygen == 0):
                    lst.append(
                        {
                            "location": c.Location,
                            "type": "oxygen",
                            "subtype": "invalid",
                            "value": c.oxygen,
                            "time": c.oxygenTime.strftime("%I:%M%p"),
                        }
                    )
            if isOffline(c.tempTime, maxOffline):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "temp",
                        "subtype": "offline",
                        "value": 0.0,
                        "time": c.tempTime.strftime("%d-%m-%y %I:%M%p"),
                    }
                )
            else:
                if not(prange.tempMin <= c.temp <= prange.tempMax) and not(c.temp == 0):
                    lst.append(
                        {
                            "location": c.Location,
                            "type": "temp",
                            "subtype": "invalid",
                            "value": c.temp,
                            "time": c.tempTime.strftime("%I:%M%p"),
                        }
                    )
            if isOffline(c.waterTime, maxOffline):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "water",
                        "subtype": "offline",
                        "value": 0.0,
                        "time": c.waterTime.strftime("%d-%m-%y %I:%M%p"),
                    }
                )
            else:
                if not(prange.waterMin <= c.water <= prange.waterMax) and not(c.water == 0):
                    lst.append(
                        {
                            "location": c.Location,
                            "type": "water",
                            "subtype": "invalid",
                            "value": c.water,
                            "time": c.waterTime.strftime("%I:%M%p"),
                        }
                    )
            if isOffline(c.salinityTime, maxOffline):
                lst.append(
                    {
                        "location": c.Location,
                        "type": "salinity",
                        "subtype": "offline",
                        "value": 0.0,
                        "time": c.salinityTime.strftime("%d-%m-%y %I:%M%p"),
                    }
                )
            else:
                if not(prange.salinityMin <= c.salinity <= prange.salinityMax) and not(c.salinity == 0):
                    lst.append(
                        {
                            "location": c.Location,
                            "type": "salinity",
                            "subtype": "invalid",
                            "value": c.salinity,
                            "time": c.salinityTime.strftime("%I:%M%p"),
                        }
                    )

    return lst


def isOffline(lastDate, maxOffline):
    timeDiff = dt.now() - lastDate
    minDiff = timeDiff.seconds//60 if timeDiff.days == 0 else 999
    return (minDiff > maxOffline)
