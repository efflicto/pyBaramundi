#!/usr/bin/env python
from bConnect import BConnect
import sys

b=BConnect("yourserver",443,"domain\\user","pass")

if len(sys.argv) == 2 and sys.argv[1] == "autoconf":
        print "yes"
elif len(sys.argv) == 2 and sys.argv[1] == "config":
        print 'graph_title Baramundi clients active'
        print 'graph_vlabel clients active'
        print 'graph_category Baramundi'
        print 'graph_scale no'
        print 'count.label clients active'
        print 'count.type GAUGE'
        print "count.max 200"
        print "count.min 0"
        print "count.warning 145"
        print "count.critical 150"
        print "count.info clients active"
else:
        print "count.value %s"%b.get_client_count_active()