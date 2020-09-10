'''
Esempio di uso:
mitmdump -p 8080 -w "$(date +%d.%m.%Y_%H.%M).log" --flow-detail 0 --set stream_websocket=true -s API_show.py
'''

SILENT=True

from mitmproxy import ctx
import json, sys

pr = ctx.log.info

# FILTER LISTS (host & entire url)
H = [
	"amazon",
	# "comms-telemetry-service.us-east-1.amazonaws.com"
]
U = [
	#"log",
	#"event"
]

sys.path.append('../commons/')
from util import next_name
NNAME = next_name('logged_')


def pp_dumps(obj):
	return json.dumps(
		obj,
		sort_keys=True,
		indent=4,
		separators=(',', ': ')
	)

class APIshow:
	''' Classe che effettua il log di richieste/risposte. Nel caso in cui il
	contenuto sia json, questo viene decodificato.
	'''
	def load(self, a):
		with open(NNAME, "a") as f:
                        f.write('[')
		print(f'[API_SHOW] logging on: {NNAME}')
	
	def matches(self, str, FILTER_LIST):
		for e in FILTER_LIST:
			if e in str: return True
			#if str.startswith(e) or str.endswith(e): return True
		return False

	def __init__(self):
		self.REQQ = []
		self.RESP = self.REQQ
	
	def request(self, flow):
		req = flow.request
		# pr("\nReq for %s" % req.pretty_host)
		if self.matches(req.pretty_host, H) or \
			self.matches(req.pretty_url, U):
			try:
				cont = json.loads(req.get_text()) #get_text
				ctype = 'json'
				#pr(pp_dumps(req)); pr("JSON: decoded!")
			except (json.decoder.JSONDecodeError, UnicodeDecodeError):
				cont = req.get_text() #text
				ctype = 'txt'
				if (len(req.raw_content)==0): pass #pr("EMPTY")
				elif not SILENT: pr( cont[:50] + (" ..." if len(cont)>=50 else "") )

			self.REQQ.append( {
				'phost':req.pretty_host,
				'path':req.path,
				'headers': dict(req.headers),
				'content':cont,
				'role':'request',
				'ctype':ctype
			} )
	
	def response(self, flow):
		resp = flow.response
		req  = flow.request
		if self.matches(req.pretty_host, H) or \
			self.matches(req.pretty_url, U):
			if not SILENT: print(flow.request)
			try:
				cont = json.loads(resp.get_text()) #text
				ctype = 'json'
			except (json.decoder.JSONDecodeError, UnicodeDecodeError):
				cont = resp.get_text() #text
				ctype = 'txt'
				if (len(resp.raw_content)==0): pass
				elif not SILENT: pr( cont[:50] + (" ..." if len(cont)>=50 else "") )
				
			#print(dict(resp.headers))
			self.RESP.append( {
				'phost':req.pretty_host,
				'path':req.path,
				'headers': dict(resp.headers),
				'content':cont,
				'role':'response',
				'ctype':ctype
			} )

		elif not SILENT:
			print('. ', end='')
			
	
	def done(self):
		save_file(self.REQQ, self.RESP, end=True)

	
	def clientdisconnect(self, layer):
		if save_file(self.REQQ, self.RESP):
                        self.REQQ = self.RESP = []


def save_file(req,res,end=False):
	try:
		f = open(NNAME, "a")
		if (req + res)!=[]:
			f.write(pp_dumps(req + res))
			f.write(',')
		if end: f.write('[]]')
		f.close()
		return True
	except Exception as e:
		# Questa eccez. comporta la perdita dei dati raccolti, deve essere
		# gestita meglio. Attualmente si usa pp_dumps poer permettere almeno
		# un recupero manuale dei dati.
		print(pp_dumps(req + res))
		print(e)
		return False


addons = [ APIshow() ]
