#!/usr/bin/env python
from bConnect import BConnect
import sys

b=BConnect("yourserver",443,"domain\\user","pass")

if len(sys.argv) == 2 and sys.argv[1] == "autoconf":
        print "yes"
elif len(sys.argv) == 2 and sys.argv[1] == "config":
        print 'graph_title Baramundi running jobs'
        print 'graph_vlabel Running job count'
        print 'graph_category Baramundi'
        print 'graph_scale no'
        print 'count.label Running job count'
        print 'count.type GAUGE'
        print "count.max 500"
        print "count.min 0"
        print "count.warning 100"
        print "count.critical 350"
        print "count.info Running job count"
else:
        print "count.value %s"%b.get_jobs_running_count()