'''
Questo script serve per analizzare i file generati da mitmdump quando è
lanciato col plug-in API_show.py.

Lo script legge file JSON tipo [ LIST1, LIST2, ... ] e crea una lista
LIST1 + LIST2 + ... che può poi essere analizzata.

Esempio d'uso:
	python3 analisi_json.py logged
'''

import sys, json, re, copy
from pprint import pprint
import binascii, zlib
from collections.abc import Iterable

INDENT = 4
DEBUG = False


try:
	logf =  open(sys.argv[1], 'r')
	LIST = []
	for _ in json.loads(logf.read()):
		LIST.extend(_)
	ALL  = copy.deepcopy(LIST)
except FileNotFoundError:
	print("file not found")
	sys.exit()


def secure_input(st):
    try:
        return input(st)
    except (Exception, EOFError):
        print()
        return None

def ask_field(keys):
	where = secure_input("  Where? [0...{}]\n  {}\n  >> ".format(len(keys)-1, list(enumerate(keys))))
	if where==None: return None
	return keys[int(where)]

def ask_fields(keys):
	where = secure_input("  Where? {{[0...{}] }}*\n  {}\n  >> ".format(len(keys)-1, list(enumerate(keys))))
	if where==None: return None
	return [keys[int(w)] for w in where.split() if w!='']

# -------------------------------------------------------------------------------
def pp_dumps(obj):
	return pprint(obj, indent=INDENT)

def custom_print():
	global LIST
	fields = ask_fields(list(LIST[0].keys()))
	if fields==None: return
	# TODO: PROTECT
	dup = True if input('  Print duplicate (chose y for efficiency)? [y/n]  > ')=='y' else False
	conts = [tuple(pck[_] for _ in fields) for pck in LIST]
	if not dup:
		try: conts = set(conts)
		except Exception: print('  Cannot check for duplicates: unhashable types'); return
	for c in  conts:
		for f in c:
			pprint(f, indent=INDENT)
		print()

def stats():
	global LIST
	types = {e['ctype'] for e in LIST}
	print("   TYPES:")
	for t in types:
		l = str(len([e['ctype'] for e in LIST if e['ctype']==t]))
		print(f'   | {t:10} {l}')
	print("   {:12} {}".format("TOTAL", str(len(LIST))))
	print('\n   HOSTS: {}'.format(len({e['phost'] for e in LIST})))
	
def filter():
	global LIST
	keys = list(LIST[0].keys())
	where = ask_field(keys)
	if where==None: return
	pattern = secure_input("  Pattern?\n  >> ")
	if pattern==None: return
	tmp_list = [p for p in LIST if match(pattern, p[where]) ]
	if tmp_list:
		LIST = tmp_list
	else:
		print('  EMPTY RESULT: LIST ROLLBACK')
	print('  NEW LIST HAS {} ELEMENTS'.format(len(LIST)))

def show_info():
	print('\n' + '-'*40)
	for k, v in FUNCTIONAL.items():
		print(f'\t{k:3} {v[0]}')
	print('\nCURRENT LIST HAS {} ELEMENTS\n'.format(len(LIST)) + '-' * 40)

def restore():
	global LIST
	LIST = copy.deepcopy(ALL)
	print('  NEW LIST HAS {} ELEMENTS'.format(len(LIST)))

def search_enc_all():
	for _ in LIST:
		search_encoded(_['content'])

def comp_set():
	w = ask_field(list(LIST[0].keys()))
	if w==None: return
	try:
		pp_dumps({e[w] for e in LIST})
	except TypeError:
		print(' --- Requested field is not hashable, cannot compute set :-( ---')

def print_file():
	fname = secure_input('  fname >> ')
	if fname==None: return
	with open(fname, 'a') as f:
		sys.stdout = f
		json.dumps(pprint(LIST))
		sys.stdout = sys.__stdout__
		print('  DUMPED')

FUNCTIONAL =  \
	{
		's': ('to compute a set', comp_set ),
		'st': ('for stats', stats),
		'f': ('to filter the working set', filter),
		'r': ('to restore the original set', restore),
		'p': ('to print the entire list', lambda: pp_dumps(LIST)),
		'pf':('to out the list on a file', print_file),
		'pc': ('for custom print', custom_print),
		'i': ('for this info', show_info),
		'd': ('[beta]', search_enc_all),
		'q': ('to QUIT', lambda: 0)
	}
# ----------------------------------------------------------------------------


def match(pattern, obj):
	if type(obj)==str:
		return re.match(pattern, obj, re.M | re.I)
	elif type(obj)==dict:
		for k,v in obj.items():
			if (type(k)==str and match(pattern, k)) or \
			(type(v)==str and match(pattern, v)):
				return True
		return False
		
def search_encoded(obj):
	import binascii
	import zlib
	if type(obj)==dict:
		for k,v in obj.items():
			if type(v)==str:
				try:
					#àprint(v[:10])
					bb = bytes.fromhex(v)
					print(bb)
					print('DECOMP:' , zlib.decompress(bb))
				except Exception as e: print("ignored: ", e)
				#pd(v)
			else:
				search_encoded(v)
	else:
		pass #print(obj)


show_info()
try:
	choice = secure_input('>> ')
except KeyboardInterrupt:
	print('\nbye')
	sys.exit()
while choice not in ['q']:
	try:
		if choice: FUNCTIONAL[choice][1]()
		choice = secure_input('>> ')
	except Exception:
		print(f'\n --- UNKNOWN ERROR ---')
		print(' --- Please restore (r) the list if the state appears inconsistent. ---\n')
		if DEBUG: raise
		choice = None
	except KeyboardInterrupt:
		print('\nYou\'ve done work, please use \'q\' to EXIT')
		choice = None
