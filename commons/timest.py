from time import *
import sys

for ts in sys.argv[1:]:
	print(strftime("%d-%m-%Y %X", gmtime(int(ts)/10**3)))
