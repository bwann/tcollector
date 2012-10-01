#!/usr/bin/python
"""A collector for SMART data from smartctl"""
#
# smartctl_stats.py
# 
# Grabs SMART vendor attributes for a disk/device and sends the raw value
# to TSD, tagged with the device name. This is a simple version and only
# collects data for a handful of predefined drives. Expanding this to
# auto-detect a list of drives and/or try to massage which value/raw value
# to use for a given drive is an exercise left to the user. :)
#
# Example attributes recorded (these can vary between manuf/model)
# smart.smartctl.raw_read_error_rate
# smart.smartctl.throughput_performance
# smart.smartctl.spin_up_time
# smart.smartctl.start_stop_count
# smart.smartctl.reallocated_sector_ct
# smart.smartctl.seek_error_rate 
# smart.smartctl.seek_time_performance
# smart.smartctl.power_on_hours
# smart.smartctl.spin_retry_count
# smart.smartctl.power_cycle_count
# smart.smartctl.power-off_retract_count
# smart.smartctl.load_cycle_count
# smart.smartctl.temperature_celsius
# smart.smartctl.reallocated_event_count
# ...
#
# Written by: Bryan Wann <bwann [at] wann.net>
#

import os
import subprocess
import sys
import time


def main():
    """smartctl_stat main loop"""

    # for now only worry about the usual root drives
    # figure out complicated auto detection later
    devices = ["/dev/sda", "/dev/sdb"]

    interval = 60

    while True:
        ts = int(time.time())
        tags = {}

        for device in devices:
            if not os.path.exists(device):
                continue

            smartctl = subprocess.Popen(
                       ["/usr/sbin/smartctl", "-A", device],
                       stdout=subprocess.PIPE)
            stdout, _ = smartctl.communicate()
            
            
            if smartctl:
                name_index = None
                value_index = None
                raw_value_index = None
                in_attributes = None

                for line in stdout.split("\n"):

                    # truncate '/dev/'
                    tags['device'] = (device.replace("/dev/", "")
                                      .replace("/", "_"))

                    # figure out which column contains our key names and values
                    if line.startswith("ID#"):
                        in_attributes = True
                        for idx, val in enumerate(line.split()):
                            if val == "ATTRIBUTE_NAME":
                                name_index = idx
                            if val == "VALUE":
                                value_index = idx
                            if val == "RAW_VALUE":
                                raw_value_index = idx
                        continue

                    if in_attributes:
                        # blank line, we've seen all the attributes
                        if line == "":
                          in_attributes = False
                          continue

                        attribute = line.split()
                        name = attribute[name_index].lower()
                        value = attribute[raw_value_index]

                        if name == "unknown_attribute":
                          continue

                        all_tags = " ".join("%s=%s" % (name, value)
                                      for name, value in tags.iteritems())
                        print("smart.smartctl.%s %d %s %s"
                              % (name, ts, value, all_tags))
                    else:
                        continue


            else:
                # In modes other than -A, return value could change based on
                # the drive health
                print >> sys.stderr, ("smartctl -A %s returned %r"
                                      % device, smartctl.returncode)

        sys.stdout.flush()
        time.sleep(interval)

if __name__ == "__main__":
    main()
