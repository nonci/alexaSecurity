'''
Questo script permette di copiare una intera cartella dal dispositivo Android anche nel caso
in cui ADB non abbia facoltà di connettersi come root. I file sono prima trasferiti in una cartella
temporanea, quindi sul PC.
'''

# USAGE EXAMPLE:
# python3 pull.py /data/data/com.amazon.dee.app/cache/org.chromium.android_webview dst_folder

import sys
from os.path import basename, join
import os
from ppadb.client import Client as AdbClient

# Questo percorso deve essere accessibile da non-root:
DEF_PATH = "/storage/emulated/0"

LIST = []
RESULT = -1
local_path = '/tmp/transf' if len(sys.argv)==2 else sys.argv[2]

print("Retrieving files...")

# Default is "127.0.0.1" and 5037
client = AdbClient(host="127.0.0.1", port=5037)
device = client.device("ZX1G22NQG3") # Nexus

def make_list(conn):
	global LIST
	data = conn.socket.makefile().read()
	LIST = data.split("\n")

l=1

def get(basedir, lpath):
	global RESULT, l, clean_up
	
	device.shell("su -C \"ls -F {} | tr -d '\\r'\"".format(basedir),
		handler=make_list)
	
	for tfile in LIST:
		if not len(tfile): break
		try:
			type, file = tfile.split(' ',1)
		except Exception as e:
			type = 'd' if tfile[-1]=='/' else '-'
			file = tfile if type=='-' else tfile[:-1]
		if type=='-':
			device.shell(f"su -c \"cp '{basedir}/{file}' '{DEF_PATH}/{file}'\"")
			device.pull(f'{DEF_PATH}/{file}', f"{lpath}/{file}")
			device.shell(f"su -C \"rm '{DEF_PATH}/{file}'\"")
			#clean_up += [f"rm {DEF_PATH}/{file}"]
			print(F"\r{l}", end='') #/RESULT
			l += 1
		elif type=='d':
			os.system(f"mkdir '{join(lpath,file)}' 2>/dev/null")
			get(join(basedir,file), join(lpath,file))


#CMD = f"ls -R -F {sys.argv[1]}  |grep -v -e 'd' |grep -v './' |grep \"- \"|wc -w"
#n_of_file = device.shell(f"su -C \"{CMD}\"", handler=out)

os.system(f"mkdir {local_path} 2> /dev/null")
get(sys.argv[1], local_path)
