#!/usr/bin/env python
#
# By: Bryan Wann <bwann@wann.net>
#
# vim: syntax=python:expandtab:shiftwidth=4:softtabstop=4:tabstop=4

"""A collector to gather channel statistics from an Arris cable modem

This parses the HTML tables from the Arris WebUI's status pages. By default
this is at 192.168.100.1 and the page is unauthenticated. This should just
work on your network even if your LAN isn't numbered 192.168.100.x, as
192.168.100.1 is "upstream" of your router.

Note: This depends on BeautifulSoup 3 (maybe works with 4?). On CentOS you'll
want to install the python-BeautifulSoup package.

Global metrics:
arris.req.time_s    How many seconds it took to fetch the status page
arris.uptime        Uptime of modem in seconds

Per channel metrics, with channel=X as a tag:
Downstream channels
arris.down.lock_status         Is channel locked/operational(1) or not(0)
arris.down.modulation          Modulation
                               (QAM256->256, QAM64->64, QAM16->16, QPSK->4)
arris.down.frequency_hz        Channel frequency, in hertz
arris.down.power_dbmvolt       Channel power, in dBmV
arris.down.snr_db              Channel signal to noise ratio, in DB
arris.down.corrected_errors    Frame errors that were correctable
arris.down.uncorrected_errors  Frame errors that were not correctable
arris.down.total_errors        Sum of correctable and non-correctable errors

Upstream channels
arris.up.lock_status           Is channel locked/operational(1) or not (0)
arris.up.channel_type          Channel type (ATDMA->1)
arris.up.channel_id            Channel id
                               (can be different than UI channel number)
arris.up.symbol_rate_ksec      Symbol rate, in kilosymbols/second
arris.up.frequency_hz          Channel frequency in hertz
arris.up.power_dbmvolt         Channel power, in dBmV

"""

import os
import re
import pwd
import sys
import time
import urllib2
from BeautifulSoup import BeautifulSoup

# If we're running as root and this user exists, we'll drop privileges.  Set this
# to 'root' if you don't want to drop privileges.
USER = "nobody"

def drop_privileges():
    """Drops privileges if running as root."""

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
    """Main loop"""

    drop_privileges()
    sys.stdin.close()

    interval = 30

    def print_stat(metric, value, tags=""):
        if value is not None:
            print "arris.%s %d %s %s" % (metric, ts, value, tags)

    def parse_swinfo(rows, table):
        for row in rows:
            cols = row.findAll('td')
            if not cols:
                continue
            cols = [ele.text.strip() for ele in cols]
            # Only parse uptime row
            if not cols[0] == 'Up Time':
                continue

            parse_uptime(cols[1])

    def parse_uptime(uptime):
        # Will this thing ever print years?
        m = re.match('(\d+)\s+days\s+(\d+)h:(\d+)m:(\d+)s',
                     uptime,
                     re.IGNORECASE)
        uptime_seconds = (
            (int(m.group(1)) * 86400) +
            (int(m.group(2)) * 3600) +
            (int(m.group(3)) * 60)
        )

        print_stat('uptime', uptime_seconds)

    def parse_table(rows, table):

        def modulation_dict(text):
            return {
                'QAM256': 256,
                'QAM64': 64,
                'QAM16': 16,
                'QPSK': 4,
            }.get(text, -1)

        def channeltype_dict(text):
            return {
                'ATDMA': 1,
            }.get(text, -1)

        # Channels in locked state
        locked_down = 0
        locked_up = 0

        for row in rows:
            cols = row.findAll('td')
            if not cols:
                continue
            cols = [ele.text.strip() for ele in cols]
            # Only parse rows with a channel number
            if not cols[0].isdigit():
                continue

            channel = cols[0]
            tags = 'channel=' + channel

            if table == 'downstream':
                lock_status = cols[1]
                modulation = modulation_dict(cols[2])
                channel_id = cols[3]
                frequency = cols[4].split()[0]
                power = cols[5].split()[0]
                snr = cols[6].split()[0]
                corrected = cols[7]
                uncorrected = cols[8]
                total_errors = corrected + uncorrected

                lock_status = '1' if lock_status == 'Locked' else '0'
                if lock_status == '1':
                    locked_down += 1

                print_stat('down.lock_status', lock_status, tags)
                print_stat('down.modulation', modulation, tags)
                print_stat('down.frequency_hz', frequency, tags)
                print_stat('down.power_dbmvolt', power, tags)
                print_stat('down.snr_db', snr, tags)
                print_stat('down.corrected_errors', corrected, tags)
                print_stat('down.uncorrected_errors', uncorrected, tags)
                print_stat('down.total_errors', uncorrected, tags)

            if table == 'upstream':
                lock_status = cols[1]          
                channel_type = channeltype_dict(cols[2])
                channel_id = cols[3]
                symbol_rate = cols[4].split()[0]
                frequency = cols[5].split()[0]
                power = cols[6].split()[0]

                lock_status = '1' if lock_status == 'Locked' else '0'
                if lock_status == '1':
                    locked_up += 1

                print_stat('up.lock_status', lock_status, tags)
                print_stat('up.channel_type', channel_type, tags)
                print_stat('up.channel_id', channel_id, tags)
                print_stat('up.symbol_rate_ksec', symbol_rate, tags)
                print_stat('up.frequency_hz', frequency, tags)
                print_stat('up.power_dbmvolt', power, tags)

        if table == 'downstream':
            print_stat('down.channels_locked', locked_down)
        if table == 'upstream':
            print_stat('up.channels_locked', locked_up)

    while True:
        ts = int(time.time())
        tags = ''

        pages = {
          'status': 'RgConnect.asp',
          'swinfo': 'RgSwInfo.asp',
        }

        for key, pagename in pages.iteritems():
            starttime = time.time()
            try:
                req = urllib2.urlopen("http://192.168.100.1/%s" % pagename)
            except urllib2.URLError, e:
                print >> sys.stderr, ("urlopen url error for %s: %s" %
                    (pagename, e.args))
            except urllib2.HTTPError, e:
                 print >> sys.stderr, ("urlopen http error for %s: %s" %
                     (pagename, e.code))
            endtime = time.time()
            reqtime = endtime - starttime

            if key == 'status':
                print_stat('req.time_s', reqtime)

            if req is not None:
                soup = BeautifulSoup(req.read())
                req.close()
                alltables = soup.findAll('table')
            
                for table in alltables:
                    headers = table.findAll('th')
                    for header in headers:
                        if key == 'status' and 'Downstream' in str(header):
                            parse_table(table.findAll('tr'),
                                        table='downstream')
                        if key == 'status' and 'Upstream' in str(header):
                            parse_table(table.findAll('tr'),
                                        table='upstream')
                        if key == 'swinfo' and 'Status' in str(header):
                            parse_swinfo(table.findAll('tr'), table='status')

            else:
                print >> sys.stderr, "modem returned http code: %s" % req.getcode()

        req.close()
        sys.stdout.flush()
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main())
