#!/opt/stack/bin/python

import ConfigParser
import requests
import stack.api
from stack.exception import *
import re
import subprocess
import sys
import os

def sub(cmd):
	p = subprocess.Popen(cmd,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		shell=True)
	(o, e) = p.communicate()
	if p.returncode == 0:
		return o
	else:
		return e

def getRepoInfo(repoid):
	r = re.compile("^[a-zA-Z\-]+[a-zA-Z]")
	s = r.search(repoid)
	r = re.compile("[0-9\.]+")
	t = r.search(repoid)
	if s:
		return s.group(0),t.group(0)

def filewrite(fname,contents):
	f = open(fname,'w')
	f.write(contents)
	f.close()

# get repo files
for r in ['hdp','ambari']:
	c = ConfigParser.RawConfigParser()
	c.read('hdp.cfg')
	vers = c.get('default', r)
	os = c.get('default','os')
	distro = c.get('default','distribution')

	# construct url to get repos
	urlbase = 'http://public-repo-1.hortonworks.com'
	if r == 'hdp':
		url = '%s/%s/%s/%s/updates/%s/%s.repo' % \
			(urlbase,r.upper(),os,distro,vers,r)
	else:
		url = '%s/%s/%s/%s/updates/%s/%s.repo' % \
			(urlbase,r,os,distro,vers,r)
	# fetch them
	rget = requests.get(url)
	if rget.status_code == 200:
		filewrite('%s.repo' % r,rget.text)
	else:
		msg = "\n%s not found.\n" % url
		msg += "Check network connectivity."
		raise stack.exception.CommandError(rget,msg)

	# read repo
	repoconfig = '%s.repo' % r
	c = ConfigParser.RawConfigParser()
	c.read(repoconfig)
	# mirror
	for repoid in c.sections():
		print("Getting %s from %s. This may take a bit..." % \
			(repoid,repoconfig))
		name,vers = getRepoInfo(repoid)
		cmd = 'stack create mirror repoconfig=/export/HDP/%s ' % repoconfig
		cmd += 'repoid=%s name=%s version=%s ' % (repoid,name,vers)
		cmd += 'newest=true'
		res = sub(cmd)
		print(res)
	# add it 
		cmd = "stack add pallet /export/HDP/%s/%s*.iso" % (repoid,repoid)
		res = sub(cmd)
		print(res)
	# enable it
		cmd = "stack enable pallet %s" % name
		res = sub(cmd)
		print(res)
