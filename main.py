import ssl
from client import Client

jid = input("JID: ")
passwd = input("Password: ")

xmpp = Client(jid, passwd)

xmpp.ssl_version = ssl.PROTOCOL_SSLv3

xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0004') # Data Forms
xmpp.register_plugin('xep_0060') # PubSub
xmpp.register_plugin('xep_0199') # XMPP Ping

# Connect to the XMPP server and start processing XMPP stanzas.
xmpp.connect()
xmpp.process()