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
        if mode == 1:
            self.add_event_handler("register", self.register) # only in the event of registry 

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("session_start", self.listen_client_requests)
        self.add_event_handler("failed_auth", self.failed_authentication)
        self.add_event_handler("message", self.message_handling)
        
        # pluggins
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # multi-user chat
        self.register_plugin('xep_0066') # Out-of-band Data
        # notifications 0085
        # notifications 0363


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
            logging.info("New account created for user %s! Now you can login with this user." % self.boundjid)
            self.disconnect()
        except IqError as e:
            # server returns an error
            logging.error("Could not register account: %s" % e.iq['error']['text'])
            self.disconnect()
        except IqTimeout:
            # connection times out
            logging.error("No response from server.")
            self.disconnect()


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
         Check your username and/or password and try again""" % self.boundjid.bare)
        self.disconnect()


    """
    Process the incoming message stanzas from the server.

    Outputs the message body to the user via command line.

    Arguments:
        msg -- Message stanza recieved from the server
    """
    def message_handling(self, msg):
        if msg['type'] in ('chat', 'normal'):
            print("[", msg['from'], "] ", msg['body'])


    """
    Get roster for the client and output into console.

    Each contact is showed in the following format:
        'name (jid) [subscription status]'
                    OR
        'jid [subscription status]'

    Arguments:
        None
    """
    def show_roster(self):
        groups = self.client_roster.groups()
        
        # get groups
        for group in groups:
            print(roster_header)
            
            # get each user inside the contact group
            for jid in groups[group]:
                sub = self.client_roster[jid]['subscription']
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print('\n %s (%s) [%s]' % (name, jid, sub))
                else:
                    print('\n %s [%s]' % (jid, sub))

                # get connections or resources added for each user
                connections = self.client_roster.presence(jid)

                if connections:
                    # output each resource and its availability
                    for res, pres in connections.items():
                        show = 'available'
                        status = 'no status'
                        
                        if pres['show']:
                            show = pres['show']

                        if pres['status']:
                            status = pres['status']
                        
                        print('   - %s (%s) (%s)' % (res, show, status))
                else:
                    print('   - OFFLINE')


    """
    Show specific user information to the client.

    Output JID and status to console.

    Arguments:
        user -- JID of the user to be shown
    """
    def user_information(self, jid):
        if jid in self.client_roster.keys():
            print(self.client_roster)

        else:
            logging.error("No user found with the specified JID")


    """
    Function for listening to client requests from the commando line.

    Reads input from the clients given a menu with the clients functionalities.
    """
    async def listen_client_requests(self, event):            
        
        while True:
            x = await aioconsole.ainput(requests_menu)
            
            try:
                x = int(x)
            except:
                x = 0
                logging.ERROR("Option invalid, choose a valid one")

            if x == 1:
                pass

            elif x == 2:
                pass

            elif x == 3:
                self.show_roster()

            elif x == 4:
                recipient = await aioconsole.ainput(request_recipient)
                message = await aioconsole.ainput(body)
                self.send_message(mto=recipient,
                    mbody=message,
                    mtype='chat'
                )

            elif x == 5:
                show = await aioconsole.ainput(request_show)
                status = await aioconsole.ainput(request_status)

                self.send_presence(pshow=show_dict[int(show)], pstatus=status)

            elif x == 6:
                jid = await aioconsole.ainput(request_username)

                self.send_presence_subscription(pto=jid)

            elif x == 7:
                jid = await aioconsole.ainput(request_username)

                self.user_information(jid)

            elif x == 8:
                logging.info("Logging out...")

                self.disconnect()
            else:
                logging.ERROR("Option invalid, choose a valid one")
