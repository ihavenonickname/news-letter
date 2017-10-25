from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy, Fault
from client.utils import ask_user, get_message, format_posts

class Subscriber():
    def __init__(self, host, port):
        self._server = ServerProxy('http://{0}:{1}'.format(host, port))
        self._user_id = None

    def _perform_login(self):
        user_id = ask_user('User identification:')

        try:
            is_registered = self._server.is_user_registered(user_id)
        except Fault as ex:
            print(get_message(ex))

            return

        if is_registered:
            self._user_id = user_id
        else:
            print('Unknown user')
            self._user_id = None

    def _create_user(self):
        user_id = ask_user('User identification:')

        try:
            self._server.register_user(user_id)
        except Fault as ex:
            print(get_message(ex))

            return

        self._user_id = user_id

    def _print_last_post(self):
        subject = ask_user('Subject:')

        post = self._server.get_last_post(subject)

        print()

        if post:
            print(format_posts([post]))
        else:
            print('No posts on this subject')

    def _print_filtered_posts(self):
        subject = ask_user('Subject:')
        min_date = ask_user('Minimum date (yyyy-MM-dd hh:mm):')
        max_date = ask_user('Maximum date (yyyy-MM-dd hh:mm):')

        try:
            posts = self._server.get_posts(subject, min_date, max_date)
        except Fault as ex:
            print(get_message(ex))

            return

        print()

        print(format_posts(posts))

    def _subscribe(self):
        subject = ask_user('Subject:')

        try:
            posts = self._server.subscribe(self._user_id, subject)
        except Fault as ex:
            print(get_message(ex))

            return

        print()

    def _watch_posts(self):
        host = ask_user('My IP:')
        port = int(ask_user('My port:'))

        def notify_new_post(post):
            print(format_posts([post]))
            print()

        try:
            rpc_server = SimpleXMLRPCServer((host, port), logRequests=False, allow_none=True)
            rpc_server.register_function(notify_new_post)

            self._server.register_listener(self._user_id, host, port)

            print('Press Ctrl-C to stop')
            print('Listening...')
            print()

            rpc_server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if rpc_server:
                rpc_server.server_close()

        self._server.unregister_listener(self._user_id)

    def _menu_before_login(self):
        print('1 - Log in into existing account')
        print('2 - Create new account and log into it')
        print('3 - Show last post')
        print('4 - List posts')

        option = ask_user('Choose an option:')

        print()

        if option == '1':
            self._perform_login()
        if option == '2':
            self._create_user()
        elif option == '3':
            self._print_last_post()
        elif option == '4':
            self._print_filtered_posts()

    def _menu_after_login(self):
        print('1 - Show last post')
        print('2 - List posts')
        print('3 - Subscribe to subject')
        print('4 - Watch new posts online')

        option = ask_user('Choose an option:')

        print()

        if option == '1':
            self._print_last_post()
        elif option == '2':
            self._print_filtered_posts()
        elif option == '3':
            self._subscribe()
        elif option == '4':
            self._watch_posts()

    def menu_loop(self):
        while True:
            if self._user_id:
                self._menu_after_login()
            else:
                self._menu_before_login()

            print()
            print('-' * 20)
            print()
