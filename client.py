
import logging
import slixmpp

class Client(slixmpp.ClientXMPP):

    """
    Slixmpp client implementation
    """
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        # event handlers
        self.add_event_handler("session_start", self.start)


    """
    Process the session_start event.

    Sends clients presence and receives de roster as confirmation.

    Arguments:
        event -- An empty dictionary.
    """
    async def start(self, event):
        self.send_presence()
        await self.get_roster()