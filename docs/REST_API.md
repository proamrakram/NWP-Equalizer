# NWP REST APIs
## Table of Contents


- [About](#about)
- [/sensor_reading](#)
- [/tankdetail](#tlocdetail)
- [/sector_pivot](#)
- [/paramstatus](#)
- [/locsummbytype](#)
- [/sectorsummbytype](#)
- [/locationstatus](#)

## About ##
The **REST** APIs return a JSON file with data from the database to by rendered by JavaScript in the browser.

## /sensor_reading ##

-  (http://127.0.0.1:5000/sensor_reading)


Methods:  POST
Receives a JSON with sensor readings submitted by an nwp controller.

    {"Controller" : int,
        "Sensor": int,
        "value": string,
        "Location": string,
        "ReadingTime": date/time (yyyy-mm-dd hh:mm)
    }
Purpose:
writes the supplied data to table model.Reading

### Notes
Location is required for readings taken manually. For autamatic readings, location is determined based on "Controller"

## /tankdetail ##
- (http://127.0.0.1:5000/api/tankdetail/<path:location>)

Return a JSON with the hourly readings for specified location.

### Parameters
*path* : **string**

Location ID eg 'L01T03'.

### Examples

``` json
[
  {
    "Conductivity": "40496", 
    "Controller": 2, 
    "DOPS": 156.6, 
    "DOmg": "12.47", 
    "Day": "Wed, 02 Jan 2019 00:00:00 GMT", 
    "Location": "L01T03", 
    "Salinity": 39.9, 
    "Temp": "30.67", 
    "Time": "16:00", 
    "WaterLevel": null
  }, 
  {
    "Conductivity": "0", 
    "Controller": 2, 
    "DOPS": null, 
    "DOmg": "9.5", 
    "Day": "Tue, 25 Dec 2018 00:00:00 GMT", 
    "Location": "L01T03", 
    "Salinity": null, 
    "Temp": "None", 
    "Time": "23:00", 
    "WaterLevel": null
  }, 
]
```

## /sector_pivot ##
- (http://127.0.0.1:5000/api/sector_pivot/<path:sector>)

Return a JSON with the hourly readings for sector.

### Parameters
*path* : **int**

sector ID eg 3

### Examples

``` json
[
  {
    "Conductivity": "40000", 
    "Controller": 21, 
    "DOPS": null, 
    "DOmg": "None", 
    "Day": "2019-01-06", 
    "Location": "SS01", 
    "Salinity": 42.0, 
    "Sector": "3", 
    "Temp": "None", 
    "Time": "16:00", 
    "WaterLevel": 172.0
  }, 
  {
    "Conductivity": "38940", 
    "Controller": 23, 
    "DOPS": null, 
    "DOmg": "None", 
    "Day": "2019-01-06", 
    "Location": "SS03", 
    "Salinity": 41.0, 
    "Sector": "3", 
    "Temp": "None", 
    "Time": "16:00", 
    "WaterLevel": 142.5
  }, 
  {
    "Conductivity": "42323", 
    "Controller": 22, 
    "DOPS": null, 
    "DOmg": "None", 
    "Day": "2019-01-06", 
    "Location": "SS02", 
    "Salinity": 42.0, 
    "Sector": "3", 
    "Temp": "None", 
    "Time": "16:00", 
    "WaterLevel": 145.0
  }
]
```

## /paramstatus ##
- (http://127.0.0.1:5000/api/paramstatus/<path:location>)

Return a JSON with the latest readings per sensor type for specified location.

### Parameters
*path* : **string**

Location ID eg 'L01T01'.

### Examples

``` json
[
  {
    "CtrlStat": "On", 
    "DOMG": 9.1, 
    "DOPS": 145.0, 
    "ECEC": 35000.0, 
    "LocStat": "Under Prep", 
    "Temp": 25.2, 
    "WL": 155.0
  }
]
```

## /locsummbytype ##
- (http://127.0.0.1:5000/api/locsummbytype/<path:location>)

Return a JSON with the readings aggregated by sensor type for specified locatio.

### Parameters
*path* : **string**

Location ID eg 'L01T04'.

### Examples

``` json
[
  {
    "Avgr": "25.02", 
    "Location": "L01T04", 
    "Maxr": 29.3, 
    "Minr": 23.0, 
    "Readings": 39, 
    "Sensor": 16, 
    "SensorOption": "C", 
    "SensorType": "Temperature"
  }, 
  {
    "Avgr": "40.01", 
    "Location": "L01T04", 
    "Maxr": 145.0, 
    "Minr": 5.6, 
    "Readings": 31, 
    "Sensor": 28, 
    "SensorOption": "MG", 
    "SensorType": "Dissolved Oxygen"
  }, 
  {
    "Avgr": "115.9", 
    "Location": "L01T04", 
    "Maxr": 196.0, 
    "Minr": 9.1, 
    "Readings": 31, 
    "Sensor": 28, 
    "SensorOption": "PS", 
    "SensorType": "Dissolved Oxygen"
  }, 
]
```

## /sectorsummbytype ##
- (http://127.0.0.1:5000/api/sectorsummbytype/<path:sector>)

Return a JSON with the readings aggregated by sensor type for specified sector.

### Parameters
*path* : **int**

Sector ID eg 2.

### Examples

``` json
[
  {
    "Avgr": "25.48", 
    "Maxr": 32.0, 
    "Minr": 23.0, 
    "Readings": 52, 
    "Sector": "2", 
    "SensorOption": "C", 
    "SensorType": "Temperature"
  }, 
  {
    "Avgr": "32.66", 
    "Maxr": 145.0, 
    "Minr": 5.6, 
    "Readings": 42, 
    "Sector": "2", 
    "SensorOption": "MG", 
    "SensorType": "Dissolved Oxygen"
  }, 
  {
    "Avgr": "123.6", 
    "Maxr": 201.0, 
    "Minr": 9.1, 
    "Readings": 40, 
    "Sector": "2", 
    "SensorOption": "PS", 
    "SensorType": "Dissolved Oxygen"
  }, 
]
```

## /locationstatus ##
- (http://127.0.0.1:5000/api/locationstatus/<path:sector>)

Return a JSON with the number of tanks by status.

### Parameters
*path* : **int**

Sector ID eg 2.

``` json
[
  {
    "active": 3, 
    "automated": 4, 
    "stopped": 0, 
    "total": 4, 
    "under_maint": 0, 
    "under_prep": 1
  }
]
```