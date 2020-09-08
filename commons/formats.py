import zlib

__last_guessed__ = 16

# Adattata da dump_cache2
# Ritorna i dati decompressi e la parte rimasta (eventuale)
def gzip_x(data):
	global __last_guessed__
	# trying to guess wbits parameter
	for i in [__last_guessed__] + list(range(-15,48)):
		try:
			do = zlib.decompressobj(wbits=i)
			__last_guessed__ = i
			dd, ud = do.decompress(data), do.unused_data
			if len(dd)==0:
				print('<no data>')
				return (None,None)
			return (dd,ud)
		except zlib.error: pass
		except ValueError as e: raise e #print (e)
	else:
		print('Unable to guess wbits')
		return (None,None)
