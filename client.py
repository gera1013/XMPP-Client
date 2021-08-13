import logging
import slixmpp
import asyncio
import aioconsole

from threading import Thread

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
        else:
            self.add_event_handler("session_start", self.start)
            self.add_event_handler("session_start", self.listen_client_requests)
            self.add_event_handler("failed_auth", self.failed_authentication)
            self.add_event_handler("message", self.message_handling)
            self.add_event_handler("groupchat_message", self.gc_message_handling)
            self.add_event_handler("groupchat_invite", self.join_muc_room)

        # pluggins
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0077') # In-band Registration
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # multi-user chat
        self.register_plugin('xep_0066') # Out-of-band Data
        self.register_plugin('xep_0085') # notifications
        self.register_plugin('xep_0363') # files
        self.register_plugin('xep_0071') # needed for files
        self.register_plugin('xep_0128') # needed for files


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
            print("New account created for user %s! Now you can login with this user." % self.boundjid)
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
    Unregister the current account from the server.

    Arguments:
        None
    """
    async def remove_account(self):
        # info query for the request
        resp = self.Iq()

        resp['type'] = 'set'
        resp['register']['register'] = True

        try:
            # registration succesful
            await resp.send()
            print("Account removed succesfully" % self.boundjid)
            self.disconnect()
        except IqError as e:
            # server returns an error
            logging.error("Could not remove account: %s" % e.iq['error']['text'])
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
        print("\nEstablishing connection...")

        # send presence to server (required)
        self.send_presence()
        
        print("\nClient connected!")

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
    Process the incoming message stanzas from the server that come from a multi-user chat.

    Outputs the message body to the user via command line.

    Arguments:
        msg -- Message stanza recieved from the server
    """
    def gc_message_handling(self, msg):
        print("[", msg['from'], "] ", "[", msg['mucnick'], "] ", msg['body'])


    """
    Process the group chat invitations and joins the rooms.

    Arguments
         -- The room's name
    """
    def join_muc_room(self, room, nick):
        self.plugin['xep_0045'].join_muc(room, nick)


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
                        show = 'chat'
                        status = '-'
                        
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
            connections = self.client_roster.presence(jid)

            if connections:
                # output each resource and its availability
                for res, pres in connections.items():
                    show = 'chat'
                    status = '-'
                    
                    if pres['show']:
                        show = pres['show']

                    if pres['status']:
                        status = pres['status']
                    
                    print('   - %s (%s) (%s)' % (res, show, status))
            else:
                print('   - OFFLINE')

        else:
            logging.error("No user found in contacts with the specified JID")

    
    """
    Process incoming files.

    Arguments
        filename -- name of the file to be sent
        recipient -- user whom will receive the file
    """
    async def file_upload(self, filename, recipient):
        try:
            url = await self['xep_0363'].upload_file(
                filename, domain="alumchat.xyz", timeout=10
            )
        except IqTimeout:
            raise TimeoutError('Could not send message in time')
        
        logging.info('Upload successful!')

        html = (
            f'<body xmlns="http://www.w3.org/1999/xhtml">'
            f'<a href="{url}">{url}</a></body>'
        )

        message = self.make_message(mto=recipient, mbody=url, mhtml=html)
        message['oob']['url'] = url
        message.send()


    """
    Process and send the chat state notifications.

    Sends active, composing, and inactive statuses depending on what the user is doing

    Arguments:
        recipient -- user whit whom communication is being established
        status -- status to send (active, composing, inactive) 
    """
    def chat_state_notifications(self, recipient, status):
        state_notification = self.Message()
        state_notification["to"] = recipient
        state_notification["chat_state"] = status
        state_notification.send()

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
                rec = await aioconsole.ainput(request_recipient)
                fname = await aioconsole.ainput(request_filename)

                await self.file_upload(fname, rec)

            elif x == 2:
                group_name = await aioconsole.ainput(request_group_name)
                nick = await aioconsole.ainput(request_nickname)

                self.join_muc_room(group_name, nick)

                print("Succesfully joined the group %s!" % group_name)

            elif x == 3:
                self.show_roster()

            elif x == 4:
                recipient = await aioconsole.ainput(request_recipient)
                mtype = 'groupchat'
                
                if "conference" not in recipient:
                    mtype = 'chat'
                    self.chat_state_notifications(recipient, "composing") 
                
                message = await aioconsole.ainput(body)

                if "conference" not in recipient:
                    self.chat_state_notifications(recipient, "inactive")

                self.send_message(mto=recipient,
                    mbody=message,
                    mtype=mtype
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
                pass

            elif x == 9:
                print("Logging out...")

                self.disconnect()

                break
            else:
                logging.ERROR("Option invalid, choose a valid one")

        quit()
