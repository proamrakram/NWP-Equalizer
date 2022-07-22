import logging
from logging.handlers import WatchedFileHandler

sysOptions = {
	"allowReadings": True,
	"sendSMSNotification": True,
	"sendEmailNotification": True,
	"smsURL": "http://sms.malath.net.sa/httpSmsProvider.aspx",
	"smsSender": "NAQUA-IT",
	"smsUser": "robian",
	"smsPW": "robian",
}

formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s: %(message)s ')

basehandler = WatchedFileHandler("G:/Python/مشروع الاخ تركي/log/nwpapp/baselogfile.log")
basehandler.setFormatter(formatter)
baselogger = logging.getLogger(__name__)
baselogger.setLevel(logging.INFO)
baselogger.addHandler(basehandler)

debughandler = WatchedFileHandler("G:/Python/مشروع الاخ تركي/log/nwpapp/debuglogfile.log")
debughandler.setFormatter(formatter)
dname = __name__ + "de"
debuglogger = logging.getLogger(dname)
debuglogger.setLevel(logging.DEBUG)
debuglogger.addHandler(debughandler)

