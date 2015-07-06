#!/usr/bin/env python
#
# Tcollector to record electrical current and voltage from Adafruit INA219
# modules, save to TSD.
#
# This script kindly depends on scottjw's Python library at
# https://github.com/scottjw/subfact_pi_ina219
# along with 2's compliment patching.
#
# vim: syntax=python:expandtab:shiftwidth=4:softtabstop=4:tabstop=4

import os
import pwd
import sys
import time
from lib.Subfact_ina219 import INA219

# Human-readable label to i2c address mappings
ina219_modules = {
    'load': '0x40',
    'battery': '0x41',
    'solar':  '0x44',
}

USER = "nobody"
interval = 30

def drop_privileges():

    if USER == 'root':
        return

    try:
        ent = pwd.getpwnam(USER)
    except KeyError:
        return

    if os.getuid() != 0:
        return
    os.setgid(ent.pw_gid)
    os.setuid(ent.pw_uid)

def main():

    drop_privileges()
    sys.stdin.close()

    while True:
        ts = int(time.time())

        for name, address in ina219_modules.items():
            ina = INA219(address=int(address, 16))

            print ("ina219.shunt_voltage %d %.3f address=%s name=%s"
                   % (ts, ina.getShuntVoltage_mV(), address, name))
            print ("ina219.voltage %d %.3f address=%s name=%s"
                   % (ts, (ina.getBusVoltage_V() +
                           ina.getShuntVoltage_mV() / 1000), address, name))
            print ("ina219.bus_voltage %d %.3f address=%s name=%s"
                   % (ts, ina.getBusVoltage_V(), address, name))
            print ("ina219.current %d %.3f address=%s name=%s"
                   % (ts, ina.getCurrent_mA(), address, name))

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == "__main__":
    main()
