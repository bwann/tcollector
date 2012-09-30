#!/usr/bin/python
"""A collector to get electricty usage from an Insteon iMeter via SmartLinc"""
#
# smartlinc_imeter.py
#
# insteon.imeter.watt   current watt measurement
# insteon.imeter.total  total watts (counter)
#
# Tags:
# controller=           Hostname/IP address of SmartLinc controller
# device=               Insteon device id (sticker on unit)
#
# The Insteon iMeter Solo is an AC-power meter with a single measured outlet.
# It's linked via powerline network to a central controller, such as the
# Insteon SmartLinc 2412N. The 2412N has ethernet and runs a  basic web
# interface which can be used to access the current power readings of one or
# multiple iMeter devices.
# 
# With a little reverse engineering of the ajax form submission and tcpdump,
# I was able to figure out which URLs to directly fetch when polling the
# SmartLinc for iMeter power readings. This also provides a resetable
# "accumulated" power value which is basically a counter of watts.
# 
# It's worth noting this isn't the only way to do this. iMeters can also be
# accessed by controllers with a USB interface, or some controllers can record
# iMeter readings in CSVs. These cases aren't covered here.
#
# Written by Bryan Wann <bwann [at] wann.net>

import os
import sys
import time
import pwd
from urllib import urlopen

# If we're running as root and this user exists, we'll drop privileges
USER = "nobody"
imeters = {}

def drop_privileges():
    try:
        ent = pwd.getpwnam(USER)
    except KeyError:
        return

    if os.getuid() != 0:
        return

    os.setgid(ent.pw_gid)
    os.setuid(ent.pw_uid)

def poll_smartlinc(address, device):
    """Makes an HTTP request to a Smartlinc controller for a given device,
    returns watts and accumulated watts
    """

    # http:///i.js  iUpdateStatusB() for byte parsing, returns
    #  watts in 'ans4' CSS element
    # http://www.smarthome.com/forum/topic.asp?TOPIC_ID=7722
    # http://www.insteon.net/pdf/2423A1_iMeter_Solo_20110211.pdf
    #  (only covers return commands of < 1.15 units?)
    #
    # 0262    Direct Command Flag
    # 198687  Device ID
    # 0F      Standard Direct (SD) Flag
    # 82      Cmd1: Get iMeter Status
    # 00      Cmd2: (don't care value 0x00 - 0xFF)
    # =I=3    Trailer??

    # send our command request
    url = "http://" + address + "/3?0262" + device + "0F8200=I=3"
    req = urlopen(url).read()
    if req is None:
      return
    # fetch the buffer for the response
    buffer = urlopen("http://" + address + "/buffstatus.xml").read()

    if buffer == "<response><BS></BS></response>":
        # response buffer empty
        return

    buffer = (buffer.replace("<response><BS>", "" )
              .replace("</BS></response>", ""))

    # make sure the expected response is in the right spot
    if buffer[41:44] == "251":
        r_device = buffer[44:50]
        r_cmd = buffer[58:60]
        r_true = int(buffer[74:78],16)
        r_total = int(buffer[78:86],16)
        return [ r_true, r_total ]

    return

def main():
    """smartlin_imeter main loop"""
    drop_privileges()

    interval = 15

    config_file = os.path.dirname(sys.argv[0]) + "/../etc/imeter.conf"
    if not os.path.exists(config_file):
        sys.exit(13)

    config = open(config_file)
    for line in config:
        if line.startswith('#'):
            continue

        [addr, deviceid] = line.split()

        try:
            imeters[addr].append(deviceid)
        except KeyError:
            imeters[addr] = [deviceid]

    while True:
        ts = int(time.time())
        # this should be parallellized to poll multiple smartlincs at once
        # in case you have more devices than you can serially poll in an
        # interval!
        for addr in imeters:
            for deviceid in imeters[addr]:
                data = poll_smartlinc( addr, deviceid )
                if data:
                    [ watts, total ] = data
                    print ("insteon.imeter.watt %s %d controller=%s device=%s"
                    % ( ts, watts, addr, deviceid ))
                    print ("insteon.imeter.total %s %d controller=%s device=%s"
                    % ( ts, total, addr, deviceid ))

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == "__main__":
    main()
