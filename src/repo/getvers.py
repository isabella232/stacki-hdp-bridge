#!/opt/stack/bin/python

import re
import sys

reponame = sys.argv[1]
r = re.compile("[0-9\.]+")
s = r.search(reponame)
if s:
	print s.group(0)
