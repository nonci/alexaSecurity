# python3 dump_cache2.py cache [db1c3f3d27fc5004_1 [prova]]
# ... <cache_files_folder> <cache_single_file_or_"ALL"> <out_dir> (default=./dumped)
# eg: python3 dump_cache2.py retrieved/org.chromium.android_webview ALL prove_01

import asn1crypto as a1c
from asn1crypto.core import Sequence
import sys
import zlib
from os import listdir
import os
from os.path import join, isdir
from subprocess import run as system
from struct import pack

sys.path.append('../commons/')
import util

LE = "little"
DUMP_LEVEL = 'std' # Use: std or all or file_only

cache_folder = sys.argv[1]
dst_file = sys.argv[2] #if len(sys.argv)>=3 else None

# ------------------------------------------------------------------------
# To store the wbit paramter found:
last_guessed = 16

# Ritorna len(dati decompressi), len(dati lasciati)
def gzip(data, out_file=None):
	global last_guessed
	if data[0:2]==b'\x1F\x8B':
		# trying to guess wbits parameter
		for i in [last_guessed] + list(range(-15,48)):
			try:
				do = zlib.decompressobj(wbits=i)
				last_guessed = i
				dd, ud = do.decompress(data), do.unused_data #[52:]
				if len(dd)==0: print('<no data>'); break
				if out_file: out_file.write(dd)
				print('unzipped')
				assert(len(ud)==0)
				return len(dd), len(ud)
			except zlib.error: pass
		else:
			print('Unable to guess wbits')
	else:
		print('no-zip data, writing as-is on ', out_file)
		if out_file: out_file.write(data)
		return 0, len(data)
# ------------------------------------------------------------------------


FOOTER = b'\xD8\x41\x0D\x97\x45\x6F\xFA\xF4'

def file_dump(fname, complete=True, handler=gzip, out_file_prefix='dumped/'):
	with open(join(cache_folder, fname), 'rb') as f:
		print(f"\n===== {fname} =====", file=sys.stderr)
		data = f.read()
	i = int.from_bytes(data[12:16], LE)  # Url Len
	url = str(data[24:24+i])[2:-1]
	print(
		util.text_on_line(url, util.console_size()[0], '|'),
		file=sys.stderr
	)
	basename = out_file_prefix+fname
	eoc = re.search(FOOTER, data).start() # end of content
	# BUG?: cannot use data[...]:
	starts = [_.start() for _ in re.finditer(b'\x30\x82',data) if _.start()>eoc+52] #possib.certif.start
	if handler:
		with open(f'{basename}_tmp', 'ab') as f1,\
			open(f'{basename}_answer', 'ab') as f2:
			m, n = handler(data[(24+i):eoc], out_file=f1)  # starts[0]
			# print(data[eoc:])
			if data[eoc+52:]:
				dissected, mime, _ = http_dissect(data[eoc+52:])
				f2.write(dissected)
			else: print('no associated response data')
			real_name = re.search(r'/([^/\?]+)(\?.*)?$',url)[1][-150:] # -150 cut to avoid OsError
			ext = MIME[mime] if '.' not in real_name else ''
			if m>0 or n>0:
				os.rename(f'{basename}_tmp', f'{basename}_{real_name}{ext}')
		if m<=0 and n<=0: os.remove(f'{basename}_tmp')
		#if n<=0: os.remove(f'{basename}_answer')
		end = i = 0
		for start in starts:
			if start<end: continue
			parsed = Sequence.load(data[start:]).dump()
			end = start+len(parsed)
			with open(f'{basename}_cert{i}.der','wb') as ce:
				ce.write(parsed)
			i+=1
		#if system("openssl x509 -inform DER -noout -text", shell=True, input=data[start:end]).returncode==0:
		if DUMP_LEVEL=='all':
			with open(f'{basename}_the_rest','wb') as tr: tr.write(data[end:])

from scapy.all import load_layer, IP, Ether, raw, wrpcap
load_layer("http")

def http_dissect(data):
	zz = b'\x00\x00'
	sep = b'\n'  # NB!!! Usare \r\n per ripristinare header HTTP come output
	h, p = data.split(zz, 1)
	h = h.replace(b'\x00', sep)
	# new_data = h + sep + sep + p
	# body = req.do_dissect(new_data)
	lis = re.split('[\n\t\r ;]', h.decode('utf-8'))
	try: ftype = lis[lis.index("Content-Type:")+1]
	except ValueError: ftype=None
	return h, ftype, p


with open('MIME.txt', 'r') as mimefile:
	MIME = {l.split()[-1]:l.split()[0] for l in mimefile.readlines()}
	MIME[None] = 'UNK'

if dst_file!='ALL':
	file_dump(dst_file, out_file_prefix=sys.argv[3]+'/')
else:
	for fn in [_ for _ in listdir(cache_folder) if not isdir(join(cache_folder,_)) and _!='index']:
		file_dump(fn, handler=gzip, out_file_prefix=sys.argv[3]+'/') #(None if fn.endswith("1") else gzip)
