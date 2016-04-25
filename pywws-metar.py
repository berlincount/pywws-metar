#!/usr/bin/env python
import paho.mqtt.client as mqtt
import os
import sys
import json
from pprint import pprint
from math import ceil, floor
import datetime

if not 'AIRPORT_CODE' in os.environ:
    os.environ['AIRPORT_CODE'] = 'XXXX'

def on_connect(client, userdata, flags, rc):
    # print("Connected with result code " + str(rc))
    client.subscribe("/weather/pywws")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    #pprint(data)
    idx = datetime.datetime.strptime(data['idx'], "%Y-%m-%d %H:%M:%S")

    metar = os.environ['AIRPORT_CODE']
    # u'idx': u'2016-04-25 20:50:59',
    metar += idx.strftime(' %d%H%MZ AUTO')

    # u'hum_in': 42,
    # u'hum_out': 54,
    # u'rel_pressue': 1002.4,

    if 'wind_dir' in data:
        # u'wind_dir': 180,
        metar += ' %03d' % round(data['wind_dir'],-1)
        # u'wind_ave_kn': 10.5,
        if 'wind_ave_kn' in data:
            metar += '%02d' % ceil(data['wind_ave_kn'])
            # u'wind_gust_kn': 11.86}
            if 'wind_gust_kn' in data and ceil(data['wind_ave_kn']) < ceil(data['wind_gust_kn']):
                metar += 'G%02d' % ceil(data['wind_gust_kn'])
        else:
            metar += '00'
        metar += 'KT'

    if 'rain' in data:
        if data['rain'] > 1:
            metar += ' RA'
        elif data['rain'] > 0:
            metar += ' -RA'

    # u'temp_out': 5.6,
    # u'dew_point': -3.0,
    if 'temp_out' in data:
        metar += ' '
        if data['temp_out'] < 0:
            data['temp_out'] *= -1
            metar += 'M'
        metar += '%02d/' % round(data['temp_out'])
        if data['dew_point'] < 0:
            data['dew_point'] *= -1
            metar += 'M'
        metar += '%02d' % round(data['dew_point'])

    # u'rain': 0,
    if 'rel_pressue' in data:
        metar += ' Q%04d' % floor(data['rel_pressue'])

    # u'rain_day': 0.3,
    if 'rain' in data and data['rain'] == 0 and 'rain_day' in data and data['rain_day'] != 0:
        metar += ' RERA'

    # That's it!
    metar += '='
    print(metar)
    sys.exit(0)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

client.loop_forever()
