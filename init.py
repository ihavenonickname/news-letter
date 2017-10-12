import sys
from client.Publisher import Publisher
from client.Subscriber import Subscriber
from server.Server import Server

def main():
    args = sys.argv[1:]

    if len(args) != 3:
        print('python init.py [publisher|subscriber|server] <host> <port>')

        return

    host = args[1]
    port = int(args[2])

    if args[0] == 'publisher':
        client = Publisher(host, port)

        try:
            client.menu_loop()
        except KeyboardInterrupt:
            print('\nBye')

        return

    if args[0] == 'subscriber':
        client = Subscriber(host, port)

        try:
            client.menu_loop()
        except KeyboardInterrupt:
            print('\nBye')

        return

    if args[0] == 'server':
        server = Server('server/newsletter.db')

        print('Serving...')

        try:
            server.serve(host, port)
        except KeyboardInterrupt:
            print('\nBye')

        return

    print('Bad argument')

if __name__ == '__main__':
    main()
