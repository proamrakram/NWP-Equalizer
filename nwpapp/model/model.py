from . import db

class ComponentType(db.Model):
    __tablename__ = "componenttype"
    id = db.Column(db.Integer, primary_key=True)
    Description = db.Column("Description", db.String(50))


class ControllerStatus(db.Model):
    __tablename__ = "ctlstatus"
    Status = db.Column("Status", db.Integer, primary_key=True)
    Description = db.Column("Description", db.NVARCHAR(50))
    controllers = db.relationship("Controller", back_populates="status")


class ControllerVersion(db.Model):
    __tablename__ = "controller_version"
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.NVARCHAR(10), unique=True)
    description = db.Column(db.NVARCHAR(50))
    version_date = db.Column(db.DateTime)
    state = db.Column(db.NVARCHAR(10))


class SensorStatus(db.Model):
    __tablename__ = "sensorstatus"
    Status = db.Column("Status", db.Integer, primary_key=True)
    Description = db.Column("Description", db.NVARCHAR(50))
    sensors = db.relationship("Sensor", back_populates="status")


class SensorType(db.Model):
    __tablename__ = "sensortype"
    SensorType = db.Column("SensorType", db.Integer, primary_key=True)
    Description = db.Column("Description", db.NVARCHAR(50))
    sensors = db.relationship("Sensor", back_populates="sensortype")


class LocStatus(db.Model):
    __tablename__ = "locstatus"
    LocStatus = db.Column("LocStatus", db.Integer, primary_key=True)
    Description = db.Column("Description", db.NVARCHAR(50))
    locations = db.relationship("Location", back_populates="status")


class Sector(db.Model):
    __tablename__ = "sector"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.VARCHAR(20), unique=True)
    description = db.Column(db.NVARCHAR(50))
    locations = db.relationship("Location", back_populates="rsector")


class Location(db.Model):
    __tablename__ = "location"
    Location = db.Column("Location", db.VARCHAR(10), primary_key=True)
    Description = db.Column("Description", db.NVARCHAR(50))
    Sector = db.Column("Sector", db.Integer, db.ForeignKey("sector.id"))
    Loc_status = db.Column("Loc_status", db.Integer, db.ForeignKey("locstatus.LocStatus"))
    Specs = db.Column("Specs", db.String(45))
    Automated = db.Column("Automated", db.Boolean)
    lastDate = db.Column("lastDate", db.DateTime)
    oxygen = db.Column("oxygen", db.Float)
    oxygenTime = db.Column("oxygenTime", db.DateTime)
    temp = db.Column("temp", db.Float)
    tempTime = db.Column("tempTime", db.DateTime)
    water = db.Column("water", db.Float)
    waterTime = db.Column("waterTime", db.DateTime)
    salinity = db.Column("salinity", db.Float)
    salinityTime = db.Column("salinityTime", db.DateTime)
    controllers = db.relationship("Controller", back_populates="location")
    status = db.relationship("LocStatus", back_populates="locations")
    rsector = db.relationship("Sector", back_populates="locations")


class Controller(db.Model):
    __tablename__ = "controller"
    id = db.Column(db.Integer, primary_key=True)
    Version = db.Column("Version", db.VARCHAR(10))
    Loc_Id = db.Column("Loc_Id", db.VARCHAR(10), db.ForeignKey("location.Location"))
    DateManuf = db.Column("DateManuf", db.DateTime)
    FirmwareVersion = db.Column("FirmwareVersion", db.VARCHAR(10))
    InfoText = db.Column("InfoText", db.NVARCHAR(100))
    StatusCd = db.Column("StatusCd", db.Integer, db.ForeignKey("ctlstatus.Status"))
    IPAddress = db.Column("ipaddress", db.String(45))
    RPiID = db.Column("rpi", db.String(10))
    LastPoke = db.Column("lastpoke", db.DateTime)
    status = db.relationship("ControllerStatus", back_populates="controllers")
    location = db.relationship("Location", back_populates="controllers")
    readings = db.relationship("Reading", back_populates="controlunit")
    components = db.relationship("CtlConfig", back_populates="controller")
    sensors = db.relationship("Sensor", back_populates="controller")
    loggederrors = db.relationship("ErrorLog", back_populates="controller")


#    lochourlyreadings = db.relationship("LocHourlyReading", back_populates = "controller")


class Model(db.Model):
    __tablename__ = "model"
    BrandModel = db.Column("BrandModel", db.VARCHAR(50), primary_key=True)
    Brand = db.Column("Brand", db.VARCHAR(20))
    Model = db.Column("Model", db.VARCHAR(20))
    Description = db.Column("Description", db.NVARCHAR(50))
    sensors = db.relationship("Sensor", back_populates="model")


class Sensor(db.Model):
    __tablename__ = "sensor"
    id = db.Column(db.Integer, primary_key=True)
    S_Type = db.Column("S_Type", db.Integer, db.ForeignKey("sensortype.SensorType"))
    Description = db.Column("Description", db.String(50))
    BrandModel = db.Column("BrandModel", db.String(50), db.ForeignKey("model.BrandModel"))
    Controller = db.Column("Controller", db.Integer, db.ForeignKey("controller.id"))
    SerialNo = db.Column("SerialNo", db.String(45))
    StatusCd = db.Column("StatusCd", db.Integer, db.ForeignKey("sensorstatus.Status"))
    readings = db.relationship("Reading", back_populates="sensor")
    status = db.relationship("SensorStatus", back_populates="sensors")
    model = db.relationship("Model", back_populates="sensors")
    sensortype = db.relationship("SensorType", back_populates="sensors")
    controller = db.relationship("Controller", back_populates="sensors")
    loggederrors = db.relationship("ErrorLog", back_populates="sensor")


class Reading(db.Model):
    __tablename__ = "reading"
    id = db.Column(db.Integer, primary_key=True)
    Controller = db.Column("Controller", db.Integer, db.ForeignKey("controller.id"))
    Sensor = db.Column("Sensor", db.Integer, db.ForeignKey("sensor.id"))
    SensorOption = db.Column("SensorOption", db.String(5))
    value = db.Column(db.Float)
    Location = db.Column("Location", db.String(10), db.ForeignKey("location.Location"))
    ReadingTime = db.Column("ReadingTime", db.DateTime)
    logtime = db.Column(db.TIMESTAMP)
    sensor = db.relationship("Sensor", back_populates="readings")
    controlunit = db.relationship("Controller", back_populates="readings")

    def to_dict(self):
        data = {
            "RecNo": self.id,
            "Controller": self.Controller,
            "Sensor": self.Sensor,
            "SensorOption": self.SensorOption,
            "Tank": self.Location,
            "Time": self.ReadingTime,
            "Value": self.value,
        }
        return data

    def from_dict(self, data):
        for field in [
            "Controller",
            "Sensor",
            "ReadingTime",
            "SensorOption",
            "value",
        ]:
            if field in data:
                setattr(self, field, data[field])


class ParamRange(db.Model):
    __tablename__ = "paramrange"
    sector = db.Column("sector", db.Integer, primary_key = True)
    oxygenMin = db.Column("oxygenMin", db.Float)
    oxygenMax = db.Column("oxygenMax", db.Float)
    tempMin = db.Column("tempMin", db.Float)
    tempMax = db.Column("tempMax", db.Float)
    waterMin = db.Column("waterMin", db.Float)
    waterMax = db.Column("waterMax", db.Float)
    salinityMin = db.Column("salinityMin", db.Float)
    salinityMax = db.Column("salinityMax", db.Float)
    maxOfflineAuto = db.Column("maxOfflineAuto", db.Integer)
    maxOfflineManual = db.Column("maxOfflineManual", db.Integer)


class ErrorLog(db.Model):
    __tablename__ = "log_ctrl"
    id = db.Column(db.Integer, primary_key = True)
    Controller = db.Column("controller", db.Integer, db.ForeignKey("controller.id"))
    Sensor = db.Column("sensor", db.Integer, db.ForeignKey("sensor.id"))
    Description = db.Column("description", db.String(100))
    ErrorTime = db.Column("errortime", db.DateTime)
    LogTime = db.Column("logtime", db.TIMESTAMP)
    controller = db.relationship("Controller", back_populates="loggederrors")
    sensor = db.relationship("Sensor", back_populates="loggederrors")


class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key = True)
    location = db.Column("location", db.VARCHAR(10))
    eventTime = db.Column("eventTime", db.DateTime)
    user = db.Column("user", db.VARCHAR(20))
    mobile = db.Column("mobile", db.VARCHAR(20))


class CtlConfig(db.Model):
    __tablename__ = "ctlconfig"
    id = db.Column(db.Integer, primary_key=True)
    Controller_Id = db.Column("Controller_Id", db.Integer, db.ForeignKey("controller.id"))
    Component_Type = db.Column("Component_Type", db.Integer)
    Qty = db.Column("Qty", db.Integer)
    controller = db.relationship("Controller", back_populates="components")


class LocSummByType(db.Model):
    __tablename__ = "vrdgbyloc"
    Sensor = db.Column("Sensor",db.Integer, primary_key=True)
    SensorOption = db.Column("SensorOption",db.Integer, primary_key=True)
    SensorType = db.Column("SensorType", db.VARCHAR(10))
    Location = db.Column("Location",db.VARCHAR(10))
    Sector = db.Column("Sector",db.Integer)
    Readings = db.Column("Readings", db.VARCHAR(10))
    Minr = db.Column("Minr",db.Integer)
    Maxr = db.Column("Maxr",db.Integer)
    Avgr = db.Column("Avgr",db.Float)


class SectorSummByType(db.Model):
    __tablename__ = "vrdgbysector"
    Sector = db.Column("Sector", db.Integer,primary_key=True)
    S_Type = db.Column("S_Type", db.VARCHAR(10) ,primary_key=True)
    SensorOption = db.Column("SensorOption",db.Integer , primary_key=True)
    SensorType = db.Column("SensorType", db.VARCHAR(10))
    Readings = db.Column("Readings",db.VARCHAR(10))
    Minr = db.Column("Minr",db.Integer)
    Maxr = db.Column("Maxr",db.Integer)
    Avgr = db.Column("Avgr",db.Float)


class LocHourlyReading(db.Model):
    __tablename__ = "vreadingspivot"
    Controller = db.Column("Controller", db.VARCHAR(10) , primary_key=True)
    rdate = db.Column(db.Float,primary_key=True)
    rhour = db.Column(db.Float,primary_key=True)
    Location = db.Column("Location",db.VARCHAR(10))
    Sector = db.Column("Sector", db.Integer)
    DO_MG = db.Column("DO_MG", db.Float)
    DO_PS = db.Column("DO_PS", db.Float)
    EC_S = db.Column("EC_S", db.Float)
    EC_EC = db.Column("EC_EC", db.Float)
    EC_SG = db.Column("EC_SG", db.Float)
    T_C = db.Column("T_C", db.Float)
    T_F = db.Column("T_F", db.Float)
    WL_US = db.Column("WL_US", db.Float)
    WL_PS = db.Column("WL_PS", db.Float)
    pH = db.Column("pH", db.Float)
