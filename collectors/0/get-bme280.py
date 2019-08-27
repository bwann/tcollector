#!/usr/bin/env python
#
# OpenTSDB tcollector for the BME280 temp/pressure/humidity/air quality sensor.
# This only collects data for temperature, humidity, and barometric pressure.
# It does not take into account the gas sensor/air quality information.
#
# Sensor: https://www.adafruit.com/product/2652
#
# Requires the RPi.bme280 library to be installed:
# https://pypi.org/project/RPi.bme280/
#   e.g. pip install RPi.bme280
#
# This was written for use with a Raspberry Pi and the BME280 sensor connected
# to the Pi via I2C.  I2C will need to be enabled in the kernel,
#   e.g. in /boot/config.txt, "dtparam=i2c_arm=on"
# This will not work with the BME680 sensor, as it uses a different Python
# library.
#
# Emitted metrics:
#   bme280.temp_c         Temperature in Celcius (C)
#   bme280.temp_f         Temperature in Fahrenheit (F)
#   bme280.pressure_hpa   Barometric pressure in Hectopascals (hPa)
#   bme280.pressure_inch  Barometric pressure in Inch of Mercury (inHg)
#   bme280.humid           Humidity, percentage
#
# By: Bryan Wann
#
# vim: syntax=python:expandtab:shiftwidth=4:softtabstop=4:tabstop=4

import bme280
import smbus2
import sys
import time

# I2C port and address
port = 1
address = 0x77
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

def main():

    interval = 15

    while True:
        ts = int(time.time())

        data = bme280.sample(bus, address, calibration_params)

        if data:
            temp_c = data.temperature
            temp_f = 9.0/5.0 * temp_c + 32

            print "bme280.temp_c %s %.2f" % (ts, temp_c)
            print "bme280.temp_f %s %.2f" % (ts, temp_f)

            print "bme280.pressure_hpa %s %.2f" % (ts, data.pressure)
            print "bme280.pressure_inch %s %.2f" % (ts, data.pressure / 33.87)

            humidity = data.humidity
            if humidity <= 100:
                print "bme280.humid %s %.2f" % (ts, humidity)

        else:
            sleep(2)
            next

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == '__main__':
    sys.exit(main())
