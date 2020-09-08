def ioctl_GWINSZ(fd):
	import fcntl, termios, struct
	l,c = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
	return int(c), int(l)


def console_size():
	''' Ritorna (col., linee) della console attuale,
		oppure -1, -1 se non possono essere determinate
	'''
	import sys
	for i in [sys.stdin, sys.stdout, sys.stderr, 0, 1, 2]:
		try:
			return ioctl_GWINSZ(i)
		except Exception as e:
			pass
	return -1,-1


def text_on_line(txt, line_dim, cut_at='<'):
	''' Taglia il testo alla lunghezza indicata e col metodo dato
		da cut_at (<, >, <>, |)
	'''
	if len(txt)>line_dim:
		if cut_at=='<':
			return '[...] ' + txt[-line_dim+6:]
		elif cut_at=='>':
			return txt[:line_dim-6] + ' [...]'
		elif cut_at=='<>':
			half = len(txt)//2
			new_ld = (line_dim-12)//2
			return '[...] ' + txt[half-new_ld:half+new_ld+(1 if line_dim%2 else 0)] + ' [...]'
		elif cut_at=='|':
			new_ld = (line_dim-7)//2
			return txt[:new_ld] + ' [...] ' + txt[(0 if line_dim%2 else -1)-new_ld:]
	return txt

def squared_print(msg, format_pars=None):
    if format_pars:
        msg = msg.format(format_pars)
    msg_ = msg.split('\n')
    l = max([len(a) for a in msg_])
    print('=' * (l+4))
    for line in msg_:
        print('| {}{} |'.format(line, ' '*(l-len(line))))
    print('=' * (l+4))


def next_name(base, extension=''):
	import re, os
	l = []
	extension.replace('.','\.')
	for _ in os.listdir():
		m = re.fullmatch(f"{base}([0-9]+){extension}",_)
		if m: l+=[int(m[1])]
	return f'{base}{max(l)+1 if l else 0}{extension}'


def print_with_caller_info(*o, **k):
	''' Utile per ridefinire 'print' in fase di debugging '''
	from traceback import extract_stack as est
	frame = est(limit=2)[0]
	print('', end=f' [{frame.name} @ {frame.lineno}] ')
	print(*o, **k)
