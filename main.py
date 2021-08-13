import logging
from getpass import getpass
from argparse import ArgumentParser

from client import Client
from util import *


if __name__ == '__main__':
    # setup the command line arguments.
    parser = ArgumentParser()

    # output verbosity options.
    parser.add_argument("-q", "--quiet", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    parser.add_argument("-d", "--debug", help="set logging to DEBUG",
                        action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO)
    parser.add_argument("-e", "--error", help="set logging to ERROR",
                        action="store_const", dest="loglevel",
                        const=logging.ERROR, default=logging.INFO)
    
    args = parser.parse_args()

    # setup logging.
    logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)-8s %(message)s')

    # ask for the intended options
    option = int(input(start_menu))
    
    # get username and password from user input
    jid = input(start_jid)
    passwd = input(start_pass)

    # initialize the client
    xmpp = Client(jid, passwd, mode=option)
    xmpp['xep_0077'].force_registration = True

    # connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)

    # disconnect client (log out)
    quit()