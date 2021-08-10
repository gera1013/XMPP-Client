import logging
from getpass import getpass
from argparse import ArgumentParser

from client import Client


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
    
    args = parser.parse_args()

    # setup logging.
    logging.basicConfig(level=args.loglevel,
                        format='%(levelname)-8s %(message)s')

    jid = input("JID: ")
    passwd = input("Password: ")

    xmpp = Client(jid, passwd)

    # connect to the XMPP server and start processing XMPP stanzas.
    xmpp.connect()
    xmpp.process(forever=False)

    xmpp.disconnect()