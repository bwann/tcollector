tcollector
==========

Custom and exotic tcollectors for OpenTSDB

`collectors/0/chef-server.py`
  Adapts output from Facebook's chef-server-stats.rb script and inserts
  metrics into TSD for measuring Chef server components
  (https://github.com/facebook/chef-utils/blob/master/chef-server-stats)

`collectors/0/ina219_power.py` -
  Recording electrical current/voltage values via i2c and Adafruit INA219
  modules. Example, with Raspberry Pi for solar power logging.

`collectors/0/smartlinc_imeter.py` -
  Grab watt information from Insteon iMeters via the web interface of
  SmartLinc controllers and put into TSD

  (This is also my first from-scratch python script after a decade of perl!)

`collectors/0/smartctl_stat.py` -
  SMART data collector

`collectors/0/tcollector.xml` -
  Simple tcollector SMF service manifest for OpenIndiana
  (OpenSolaris/Solaris 11 too?)

Disclaimer:
I am providing code in this repository to you under an open source license.
Because this is my personal repository, the license you receive to my code
is from me and not from my employer (Facebook).

--bwann
