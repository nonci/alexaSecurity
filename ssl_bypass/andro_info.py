#! /usr/local/bin/python3

'''
Usage examples:
===============
  ./andro_info.py com.amazon.dee.app 'clas(trust)'
  ./andro_info.py com.amazon.dee.app 'meth(com.android.org.conscrypt.TrustManagerImpl)'
  ./andro_info.py com.amazon.dee.app 'over(com.android.org.conscrypt.TrustManagerImpl, checkTrusted)'
  
'''

import frida, sys, re

def load_script(js_script):
    s = session.create_script(js_script)
    s.on('message', on_message)
    s.load()
    print(f'-- script loaded --')
    return s

def on_message(message, data):
    if message['type']=='error':
        print(message['stack'])
    else:
        print("SIGNATURES LIST\n===============")
        for _ in re.findall("overload(\(.*\))",message['payload']):
            print('  '+_)

#########################################################

with open("andro_info.js") as s:
    js_script = s.read()

replace = sys.argv[2].startswith('over')

device = frida.get_device_manager().enumerate_devices()[-1]
print('-- ' + str(device) + ' --')

session = device.attach(sys.argv[1])
print('-- Attached at process --')

# We don't have to change the script:
if not replace:
    script = load_script(js_script)

try:
    first = True
    for a in sys.argv[2:]:
        inp = re.split('[\(\),]', a)[:-1]
        #print(inp)
        if replace and first:
            # then 'THE_NAME' in the script must be
            # replaced by the method name:
            js_script = js_script.replace("THE_NAME", inp[2])
            script = load_script(js_script)
            first=False
        exec(f"script.exports.{inp[0]}(*inp[1:])")
    session.detach()
except Exception as e: #KeyboardInterrupt:
    print('\nDetaching session ... ', end='')
    session.detach()
    print(f'OK ({e.args[0:2]})', end='\n\n\n')
    raise e
