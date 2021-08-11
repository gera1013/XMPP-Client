import logging
import slixmpp
import asyncio
import aioconsole

from slixmpp.exceptions import IqError, IqTimeout

from util import *


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
    def __init__(self, jid, password, mode=2):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # event handlers
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("session_start", self.listen_client_requests)
        self.add_event_handler("failed_auth", self.failed_authentication)
        
        if mode != 2:
            self.add_event_handler("register", self.register) # only in the event of registry 

        # pluggins
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # multi-user chat
        self.register_plugin('xep_0066') # Out-of-band Data
        # notifications 0085
        # notifications 0363


    """
    Process the session_start event.

    Sends clients presence and receives de roster as confirmation.

    Arguments:
        event -- An empty dictionary.
    """
    async def start(self, event):
        logging.info("Establishing connection...")

        # send presence to server (required)
        self.send_presence()

        # get roster of other clients
        await self.get_roster()


    """
    Process that handles the failed authentication event.

    Outputs the error ocurred

    Arguments:
        event -- An empty dictionary.
    """
    def failed_authentication(self, event):
        # output the error to console
        print("")
        logging.error("""Unable to login to an account with the given username: %s
         Check your username and/or password and try again""" % self.jid)
        self.disconnect()


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
        x = await aioconsole.ainput(requests_menu)
        x = int(x)

        if x == 1:
            pass

        elif x == 2:
            pass

        elif x == 3:
            pass

        elif x == 4:
            pass

        elif x == 5:
            pass

        elif x == 6:
            pass

        elif x == 7:
            logging.info("Logging out...")

            self.disconnect()
        else:
            logging.ERROR("Option invalid, choose a valid one")
