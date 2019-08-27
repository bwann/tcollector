tcollector
==========

Custom and exotic tcollectors for OpenTSDB

`collectors/0/chef-server.py` -
  Adapts output from Facebook's chef-server-stats.rb script and inserts
  metrics into TSD for measuring Chef server components
  (https://github.com/facebook/chef-utils/blob/master/chef-server-stats)

`collectors/0/arris-modem.py` -
  Collects up/downstream channel information from a Motorola/Arris cable
  modem. May be sort of brittle since I only have one model to test with.

  * Screenshot of modem status page: arris_modem_status_example.png
  * Poor man's cablemodem dashboard example: arris_modem_tcollector_example.png


`collectors/0/smartlinc_imeter.py` -
  Grab watt information from Insteon iMeters via the web interface of
  SmartLinc controllers and put into TSD. I've since moved on to Ubiquiti's
  mPower kit.

  (This is also my first from-scratch python script after a decade of perl!)

  * Screenshot of iMeter power charts: martlinc-imeter-tcollector-example.png

`collectors/0/smartctl_stat.py` -
  SMART data collector

#### Raspberry Pi-orientated tcollectors
`collectors/0/dht_temp.py` -
  Record temperature/humidity from DHT11/DHT22 digital temperature/humidity
  sensors connected via GPIO

`collectors/0/get-bme280.py` -
  Record temperature/humidity/barometric pressure from BME280 digital
  temperature/humidity/pressure/gas sensors connected via I2C

`collectors/0/ina219_power.py` -
  Recording electrical current/voltage values via i2c and Adafruit INA219
  modules. Example, with Raspberry Pi for solar power logging.

#### Solaris/OpenIndiana tcollector goodies
I've long since broken up with Solaris and not maintaining these anymore,
but keeping these around for some lost souls who may want to use it.

`chef-openindiana-smf-example.rb` -
  Example chef recipe to install the tcollector SMF manifest

`tcollector.xml` -
  Simple tcollector SMF service manifest for OpenIndiana
  (OpenSolaris/Solaris 11 too?)

### Disclaimer
I am providing code in this repository to you under an open source license.
Because this is my personal repository, the license you receive to my code
is from me and not from my employer.

Bugs? Clown town? Send me pull requests

--bwann
