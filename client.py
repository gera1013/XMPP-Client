import logging
import slixmpp
import asyncio
import aioconsole

from slixmpp.exceptions import IqError, IqTimeout

"""
Slixmpp client implementation
"""
class Client(slixmpp.ClientXMPP):

    """
    Client initialization. 

    Extends ClientXMPP.

    Arguments:
        jid -- User's JID for logging in.
        password -- User's password for logging in.
    """
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("session_start", self.listen_client_requests)
        # self.add_event_handler("register", self.register)

        # pluggins
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # multi-user chat
        self.register_plugin('xep_0066') # Out-of-band Data

    """
    Process the session_start event.

    Sends clients presence and receives de roster as confirmation.

    Arguments:
        event -- An empty dictionary.
    """
    async def start(self, event):
        self.send_presence()
        await self.get_roster()


    """
    Fill the registration form for adding new users inside a server.

    Basic registration fields (username, password, email)

    Arguments:
        iq -- Info query of the request.
    """
    async def register(self, iq):
        # info query for the request
        resp = self.Iq()

        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password

        try:
            # registration succesful
            await resp.send()
            logging.info("New account created for user %s!" % self.boundjid)
        except IqError as e:
            # server returns an error
            logging.error("Could not register account: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            # connection times out
            logging.error("No response from server.")
            self.disconnect()


    """
    Function for listening to client requests from the commando line.

    Reads input from the clients given a menu with the clients functionalities.
    """
    async def listen_client_requests(self, event):            
        await asyncio.sleep(2)
        x = await aioconsole.ainput('Ingrese algo: ')

        print(x)