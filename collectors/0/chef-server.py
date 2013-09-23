#!/usr/bin/python
"""A collector to get Chef Server stats via chef-server-stats.rb"""
#
# chef-server.rb
#
# Open-source Chef Server ("OSC") metrics:
# chef.server.num_nodes
# chef.server.num_cookbooks
# chef.server.num_roles
# chef.server.rabbitmq_messages_ready
# chef.server.postgresql_seq_scan
# chef.server.postgresql_seq_tup_read
# chef.server.postgresql_idx_scan
# chef.server.postgresql_idx_tup_fetch
# chef.server.postgresql_n_tup_ins
# chef.server.postgresql_n_tup_upd
# chef.server.postgresql_n_tup_del
# chef.server.postgresql_n_live_tup
# chef.server.postgresql_n_dead_tup
# chef.server.postgresql_connection_count
# chef.server.status
#
# Private Chef Server ("OPC") metrics:
#

import json
import os
import pwd
import subprocess
import sys
import time


def main():
  """collector main loop"""

  # Don't run if we don't have Chef knife or the stat script
  if not os.path.exists("/usr/bin/knife"):
    sys.exit(13)
  if not os.path.exists("/root/chef-server-stats.rb"):
    sys.exit(13)

  interval = 30

  while True:
    ts = int(time.time())

    stats = subprocess.Popen(
      [ 'knife', 'exec', '/root/chef-server-stats.rb' ],
      stdin=None, stdout=subprocess.PIPE, bufsize=1)
    ( out, err ) = stats.communicate()

    if stats.returncode == 0:
      stats_json = json.loads(out, encoding='utf-8')
      #print json.dumps(stats_json, sort_keys=True, indent=4, separators=(',', ': '))
      for metric in stats_json:
        if metric.startswith('chef.server'):
          print ("%s %d %s" % (metric, ts, stats_json[metric]))

    sys.stdout.flush()
    time.sleep(interval)

if __name__ == '__main__':
  main()
