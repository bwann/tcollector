#!/usr/bin/env python
#
# OpenTSDB tcollector for Adafruit DHT22/AM2302 digitial humidity and
# temperature sensors.
#
# Sensor: https://www.adafruit.com/product/385
#
# Requires the Adafruit_Python_DHT Python library to be installed:
# https://github.com/adafruit/Adafruit_Python_DHT.git
#
# This was written for use with Raspberry Pis and the DHT sensor connected to
# the Pi via GPIO4 (pin 7), but can work with any GPIO by updating the 'gpio'
# variable below.  This also works fine with the less-precise DHT11 sensor.
#
# Emitted metrics, with sensor=X as a tag:
#   dht.temp_c         Temperature in Celcius (C)
#   dht.temp_f         Temperature in Fahrenheit (F)
#   dht.humid          Humidity, percentage
#
# By: Bryan Wann
#
# TODO:
# - Make this support reading multiple sensors from the same Raspberry Pi
#
# vim: syntax=python:expandtab:shiftwidth=4:softtabstop=4:tabstop=4

import Adafruit_DHT
import sys
import time

# DHT22/AM2302 sensor, GPIO4 pin on Raspberry Pi
gpio = 4
# Sensor name, emitted as sensor=X as a tag
sensor = 'wall'

def main():

    # Note: Adafruit_DHT library doesn't support reads faster than
    # every 2 seconds
    interval = 30

    while True:
        ts = int(time.time())

        humidity, temp_c = Adafruit_DHT.read_retry(22, gpio)

        if temp_c:
            temp_f = 9.0/5.0 * temp_c + 32
            print "dht.temp_c %s %.2f sensor=%s" % (ts, temp_c, sensor)
            print "dht.temp_f %s %.2f sensor=%s" % (ts, temp_f, sensor)

        if humidity <= 100:
            print "dht.humid %s %.2f sensor=%s" % (ts, humidity, sensor)

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == '__main__':
    sys.exit(main())
