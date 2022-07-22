#transmit water parameter reading to the website via API
import requests, datetime as dt
import time
#SERVER_URL='http://192.168.1.104:5000/api'
#SERVER_URL='http://172.18.246.224:5000/api'
SERVER_URL='http://localhost:5000/api'
def submit(controller, sensor, sensoroption, readingdate, value):
    payload = {'Controller':controller,
        'Sensor':sensor,
        'SensorOption':sensoroption,
        'ReadingTime':readingdate,
        'value':value}
#    payload = {'id':'1',
#        'desc':'descr'}
    response = requests.post(SERVER_URL+'/sensorreading',json=payload)
    print(response.text)
    print(response.status_code)
    return response
def submit_v2(controller, sensor, readingdate, value):
    payload = {'Controller':controller,
        'Sensor':sensor,
        'ReadingTime':readingdate,
        'value':value}
#    payload = {'id':'1',
#        'desc':'descr'}
    response = requests.post(SERVER_URL+'/sensor_reading',json=payload)
    print(response.text)
    print(response.status_code)
    return response
def sensorinfo():
    response = requests.get(SERVER_URL+'/sensorinfo'+'?status=1')
    print(response.text)
    print(response.status_code)
    return response
def sensorreadings(sensor = 1):
    response = requests.get(SERVER_URL+'/sensorreadings'+'?sensor=' + str(sensor))
    print(response.text)
    print(response.status_code)
    return response

strdtm=dt.datetime.now().strftime("%Y-%m-%d") + ' ' + dt.datetime.now().strftime("%H:%M") 
v = {'TDS':'138.3','EC':'38380','S':'39.2'}
#v = {'EC':'36.5','TDS':'23555'}
r=submit_v2(4,40,strdtm, v)
# time.sleep(2)
r=submit_v2(4,28,strdtm,{'MG':'13.6','PS':'196'})
# time.sleep(2)
r=submit_v2(4,16,strdtm,['29.3'])
# time.sleep(2)
r=submit_v2(4,71,strdtm,['152'])
# r=submit(17,18,''C'',strdtm,'24.0')
# r=submit(18,19,''C'',strdtm,'24.3')
# r=submit(19,20,''C'',strdtm,'24.6')
# r=submit(20,21,''C'',strdtm,'24.4')
# r=submit(21,22,''C'',strdtm,'22.7')
# r=submit(22,23,''C'',strdtm,'26.5')
# r=submit(23,24,''C'',strdtm,'26.5')
# r=submit(24,25,''C'',strdtm,'25.5')
# r=submit(25,26,''C'',strdtm,'24')
# r=submit(26,27,''C'',strdtm,'23')

# r=submit(4,16,''C'',strdtm,'23.5')
# r=submit(16,17,''C'',strdtm,'23')
# r=submit(17,18,''C'',strdtm,'24.0')
# r=submit(18,19,''C'',strdtm,'24.3')
# r=submit(19,20,''C'',strdtm,'24.6')
# r=submit(20,21,''C'',strdtm,'24.4')
# r=submit(21,22,''C'',strdtm,'22.7')
# r=submit(22,23,''C'',strdtm,'26.5')
# r=submit(23,24,''C'',strdtm,'26.5')
# r=submit(24,25,''C'',strdtm,'25.5')
# r=submit(25,26,''C'',strdtm,'24')
# r=submit(26,27,''C'',strdtm,'23')

# r=submit(4,28,'PS',strdtm,'5.6')
# r=submit(16,29,'PS',strdtm,'9.3')
# r=submit(17,30,'PS',strdtm,'9.1')
# r=submit(18,31,''C'',strdtm,'9.2')
# r=submit(19,32,''C'',strdtm,'9.1')
# r=submit(20,33,''C'',strdtm,'9')
# r=submit(21,34,''C'',strdtm,'9.5')
# r=submit(22,35,''C'',strdtm,'10')
# r=submit(23,36,''C'',strdtm,'11')
# r=submit(24,37,''C'',strdtm,'15')
# r=submit(25,38,''C'',strdtm,'14')
# r=submit(26,39,''C'',strdtm,'13')

# r=submit(4,28,''C'',strdtm,'12')
# r=submit(16,29,''C'',strdtm,'11')
# r=submit(17,30,''C'',strdtm,'13')
# r=submit(18,31,''C'',strdtm,'14')
# r=submit(19,32,''C'',strdtm,'12')
# r=submit(20,33,''C'',strdtm,'14')
# r=submit(21,34,''C'',strdtm,'15')
# r=submit(22,35,''C'',strdtm,'12')
# r=submit(23,36,''C'',strdtm,'13')
# r=submit(24,37,''C'',strdtm,'16')
# r=submit(25,38,''C'',strdtm,'13')
# r=submit(26,39,''C'',strdtm,'12')

# r=submit(4,28,'PS',strdtm,'95')
# r=submit(16,29,'PS',strdtm,'110')
# r=submit(17,30,'PS',strdtm,'111')
# r=submit(18,31,'PS',strdtm,'115')
# r=submit(19,32,'PS',strdtm,'110')
# r=submit(20,33,'PS',strdtm,'109')
# r=submit(21,34,'PS',strdtm,'120')
# r=submit(22,35,'PS',strdtm,'105')
# r=submit(23,36,'PS',strdtm,'115')
# r=submit(24,37,'PS',strdtm,'200')
# r=submit(25,38,'PS',strdtm,'190')
# r=submit(26,39,'PS',strdtm,'170')

# r=submit(4,28,'PS',strdtm,'150')
# r=submit(16,29,'PS',strdtm,'150')
# r=submit(17,30,'PS',strdtm,'160')
# r=submit(18,31,'PS',strdtm,'170')
# r=submit(19,32,'PS',strdtm,'150')
# r=submit(20,33,'PS',strdtm,'200')
# r=submit(21,34,'PS',strdtm,'201')
# r=submit(22,35,'PS',strdtm,'150')
# r=submit(23,36,'PS',strdtm,'160')
# r=submit(24,37,'PS',strdtm,'201')
# r=submit(25,38,'PS',strdtm,'150')
# r=submit(26,39,'PS',strdtm,'130')

# r=submit(4,40,'EC',strdtm,'39000')
# r=submit(16,41,'EC',strdtm,'39200')
# r=submit(17,42,'EC',strdtm,'39390')
# r=submit(18,43,'EC',strdtm,'40023')
# r=submit(19,44,'EC',strdtm,'42000')
# r=submit(20,45,'EC',strdtm,'40233')
# r=submit(21,46,'EC',strdtm,'40000')
# r=submit(22,47,'EC',strdtm,'42323')
# r=submit(23,48,'EC',strdtm,'38940')
# r=submit(24,49,'EC',strdtm,'40002')
# r=submit(25,50,'EC',strdtm,'43500')
# r=submit(26,51,'EC',strdtm,'39500')

# r=submit(4,40,'S',strdtm,'38')
# r=submit(16,41,'S',strdtm,'35')
# r=submit(17,42,'S',strdtm,'39')
# r=submit(18,43,'S',strdtm,'40')
# r=submit(19,44,'S',strdtm,'40')
# r=submit(20,45,'S',strdtm,'42')
# r=submit(21,46,'S',strdtm,'42')
# r=submit(22,47,'S',strdtm,'42')
# r=submit(23,48,'S',strdtm,'41')
# r=submit(24,49,'S',strdtm,'41')
# r=submit(25,50,'S',strdtm,'42')
# r=submit(26,51,'S',strdtm,'42')

# r=submit(4,71,'US',strdtm,'155')
# r=submit(16,72,'US',strdtm,'155')
# r=submit(17,73,'US',strdtm,'150')
# r=submit(18,74,'US',strdtm,'150')
# r=submit(19,75,'US',strdtm,'160')
# r=submit(20,76,'US',strdtm,'167')
# r=submit(21,77,'US',strdtm,'190')
# r=submit(22,78,'US',strdtm,'180')
# r=submit(23,79,'US',strdtm,'145')
# r=submit(24,80,'US',strdtm,'145')
# r=submit(25,81,'US',strdtm,'40')
# r=submit(26,82,'US',strdtm,'45')

# r=submit(4,71,'US',strdtm,'150')
# r=submit(16,72,'US',strdtm,'195')
# r=submit(17,73,'US',strdtm,'158')
# r=submit(18,74,'US',strdtm,'152')
# r=submit(19,75,'US',strdtm,'161')
# r=submit(20,76,'US',strdtm,'160')
# r=submit(21,77,'US',strdtm,'154')
# r=submit(22,78,'US',strdtm,'110')
# r=submit(23,79,'US',strdtm,'140')
# r=submit(24,80,'US',strdtm,'166')
# r=submit(25,81,'US',strdtm,'43')
# r=submit(26,82,'US',strdtm,'48')


# r=submit(4,7,'MG',strdtm,'12.5')
# r=submit(4,7,'MG',strdtm,'11.0')
# r=submit(4,7,'MG',strdtm,'13.2')
# r=submit(4,7,'MG',strdtm,'16.6')
# r=submit(4,7,'MG',strdtm,'9')

# r=submit(2,7,'PS',strdtm,'155')
# r=submit(2,7,'PS',strdtm,'143')
# r=submit(2,7,'PS',strdtm,'163')
# r=submit(2,7,'PS',strdtm,'201')
# r=submit(2,7,'PS',strdtm,'121')

# r=submit(2,1,''C'',strdtm,'30.1')
# r=submit(2,1,''C'',strdtm,'31.3')
# r=submit(2,1,''C'',strdtm,'31')
# r=submit(2,1,''C'',strdtm,'32')
# r=submit(2,1,''C'',strdtm,'29')

# r=submit(2,10,'S',strdtm,'39')
# r=submit(2,10,'S',strdtm,'39.4')
# r=submit(2,10,'S',strdtm,'40.1')
# r=submit(2,10,'S',strdtm,'40')
# r=submit(2,10,'S',strdtm,'41')

# r=submit(2,10,'EC',strdtm,'39255')
# r=submit(2,10,'EC',strdtm,'40143')
# r=submit(2,10,'EC',strdtm,'40163')
# r=submit(2,10,'EC',strdtm,'39901')
# r=submit(2,10,'EC',strdtm,'43021')



# r=submit(3,8,'MG',strdtm,'12.5')
# r=submit(3,8,'MG',strdtm,'11.0')
# r=submit(3,8,'MG',strdtm,'13.2')
# r=submit(3,8,'MG',strdtm,'16.6')
# r=submit(3,8,'MG',strdtm,'9')

# r=submit(3,8,'PS',strdtm,'155')
# r=submit(3,8,'PS',strdtm,'143')
# r=submit(3,8,'PS',strdtm,'163')
# r=submit(3,8,'PS',strdtm,'201')
# r=submit(3,8,'PS',strdtm,'121')

# r=submit(3,2,''C'',strdtm,'30.1')
# r=submit(3,2,''C'',strdtm,'31.3')
# r=submit(3,2,''C'',strdtm,'31')
# r=submit(3,2,''C'',strdtm,'32')
# r=submit(3,2,''C'',strdtm,'29')

# r=submit(3,11,'S',strdtm,'39')
# r=submit(3,11,'S',strdtm,'39.4')
# r=submit(3,11,'S',strdtm,'40.1')
# r=submit(3,11,'S',strdtm,'40')
# r=submit(3,11,'S',strdtm,'41')

# r=submit(3,11,'EC',strdtm,'39255')
# r=submit(3,11,'EC',strdtm,'40143')
# r=submit(3,11,'EC',strdtm,'40163')
# r=submit(3,11,'EC',strdtm,'39901')
# r=submit(3,11,'EC',strdtm,'43021')

# r=submit(3,14,'',strdtm,'150')
# r=submit(3,14,'',strdtm,'155')
# r=submit(3,14,'',strdtm,'190')
# r=submit(3,14,'',strdtm,'170')
# r=submit(3,14,'',strdtm,'110')



#r = sensorreadings(14)
#r=submit(2,7,'PS',strdtm,'135')
#r = sensorinfo()