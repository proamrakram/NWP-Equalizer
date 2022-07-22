from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    IntegerField,
    RadioField,
    SelectField,
    SubmitField,
)
from wtforms import BooleanField, validators, ValidationError
from wtforms import DateField


class sector_form(FlaskForm):
    sector_name = StringField(
        "Sector Name",
        [
            validators.DataRequired(
                "Please enter short name for group of locations"
            )
        ],
    )
    sector_description = StringField(
        u"Description",
        [
            validators.DataRequired(
                "It is a good idea to add some information about sector"
            )
        ],
    )
    submit_button = SubmitField("Add")
    delete_button = SubmitField("Delete")


class location_form(FlaskForm):
    location_id = StringField(
        u"Location", [validators.DataRequired("Location ID is mandatory")]
    )
    location_description = StringField(
        u"Description",
        [validators.DataRequired("Enter some info about the location")],
    )
    sector = SelectField(u"Sector", coerce=int)
    status = SelectField(u"Status", coerce=int)
    specs = StringField(u"Specifications")
    submit_button = SubmitField("Add")
    delete_button = SubmitField("Delete")


class sensor_form(FlaskForm):
    s_id = StringField(u"SensorID")
    s_type = SelectField(u"Type", coerce=int)
    s_description = StringField(
        u"Description",
        [validators.DataRequired("Enter some info about the sensor")],
    )
    model = SelectField(u"Brand, Model")
    status = SelectField(u"Status", coerce=int)
    serial_no = StringField(u"H/w No")
    submit_button = SubmitField("Add")
    delete_button = SubmitField("Delete")


class controller_form(FlaskForm):
    c_id = StringField(u"ControllerID")
    version = SelectField(u"H/W Version", coerce=int)
    date_manuf = DateField(
        u"Date", [validators.DataRequired("Manuf. Date required")]
    )
    specs = StringField(
        u"Specs",
        [validators.DataRequired("Enter some info about the controller")],
    )
    cstatus = SelectField(u"Status", coerce=int)
    csector = SelectField(u"Sector", coerce=int)
    clocation = SelectField(u"Location")
    submit_button = SubmitField("Add")
    delete_button = SubmitField("Delete")


class manual_form(FlaskForm):
    unit = SelectField(u"Unit")
    reading_date = StringField(
        u"Date", [validators.DataRequired("Enter Date")]
    )
    reading_hour = SelectField(u"Reading Time")
    sector = SelectField(u"Sector")
    location = SelectField(u"Location")
    temp_surface = StringField(
        u"Surface Temp",
        [validators.DataRequired("Surface Temp mandatory")],
        render_kw={"placeholder": "deg 'C'"},
    )
    temp_bottom = StringField(
        u"Bottom Temp",
        [validators.Optional()],
        render_kw={"placeholder": "deg 'C'"},
    )
    DO_surface_mg = StringField(
        u"Surface DO(mg)", [validators.DataRequired("Surface DO mandatory")]
    )
    DO_bottom_mg = StringField(u"Bottom DO(mg)")
    DO_surface_saturation = StringField(
        u"Surface DO(%)", [validators.DataRequired("Surface DO mandatory")]
    )
    DO_bottom_saturation = StringField(u"Bottom DO(%)")
    salinity = StringField(
        u"Salinity", [validators.DataRequired("Salinity mandatory")]
    )
    save_button = SubmitField("save")
    update_button = SubmitField("update")


class report_form_001(FlaskForm):
    """report data selection from for 
	Tank Readings Report (001);
	Exception Report (002)
	"""

    sector = SelectField(u"Sector", coerce=int)
    location_from = SelectField(u"Tank From")
    location_to = SelectField(u"To")
    date_from = StringField(u"Date From")
    date_to = StringField(u"To")
    data_option = RadioField(
        u"Include",
        choices=[
            ("auto", "Only Auto"),
            ("manual", "Only Manual"),
            ("both", "Both"),
        ],
        default="both",
    )
    submit_button = SubmitField("Show Report")


class report_form_003(FlaskForm):
    """ Report data selection form for 
	Sensor Readings Report(003)
	"""

    sensor_id = IntegerField(
        u"Sensor", [validators.DataRequired("must enter valid sensor id")]
    )
    location_from = StringField(u"Tank From", default="")
    location_to = StringField(u"To", default="ZZZZZZ")
    controller_from = IntegerField(u"Controller From", default=1)
    controller_to = IntegerField(u"To", default=999)
    date_from = StringField(
        u"Date From", [validators.DataRequired("date range is required")]
    )
    date_to = StringField(
        u"To", [validators.DataRequired("date range is required")]
    )
    submit_button = SubmitField("Show Report")


class report_form_a001(FlaskForm):
    """ Report data selection form for 
	Controllers Report(a101)
	"""

    submit_button = SubmitField("Show Report")
