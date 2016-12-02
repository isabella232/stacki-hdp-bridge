#!/opt/stack/bin/python

import re
import sys

reponame = sys.argv[1]
r = re.compile("^[a-zA-Z\-]+[a-zA-Z]")
s = r.search(reponame)
if s:
	print s.group(0)
