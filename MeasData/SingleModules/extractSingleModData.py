#!/usr/bin/python

import os,sys,fnmatch

theDir = '.'

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

dataType = 'TSil'

moduleList = {}
outfileList = {}
for file in findfiles(theDir, '*'+dataType+'.txt'):
    f = open(file, 'rU')
    lines = f.readlines()
    f.close()
    for line in lines:
		if line.startswith('#['): 
			try: outfileList[module].close()
			except: pass
			module=line[2:-2]
			print module
			outfileList[module] = open(dataType+'/'+module+'.txt', 'w')
			outfileList[module].truncate()
			continue
		try: outfileList[module].write(line)
		except: pass

