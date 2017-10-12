from xmlrpc.client import ServerProxy, Fault
from client.utils import ask_user, get_message, format_posts

class Publisher():
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

    def _add_subject(self):
        subject_name = ask_user('Subject name:')

        try:
            posts_limit = int(ask_user('Posts limit:'))
        except ValueError:
            print('Not a valid number')

            return

        try:
            self._server.add_subject(self._user_id, subject_name, posts_limit)
        except Fault as ex:
            print(get_message(ex))

    def _print_subjects(self):
        try:
            subjects = self._server.get_subjects(self._user_id)
        except Fault as ex:
            print(get_message(ex))

            return

        def format_subject(subject):
            mask = 'Name: {0}\nPosts limit: {1}'

            return mask.format(
                subject['name'],
                subject['posts_limit']
            )

        print(*map(format_subject, subjects), sep='\n\n')

    def _add_post(self):
        subject = ask_user('Subject:')
        title = ask_user('Title:')
        body = ask_user('Body:')

        try:
            self._server.add_post(self._user_id, subject, title, body)
        except Fault as ex:
            print(get_message(ex))

    def _print_posts(self):
        try:
            posts = self._server.get_all_posts(self._user_id)
        except Fault as ex:
            print(get_message(ex))

            return

        print(format_posts(posts))

    def _menu_after_login(self):
        print('1 - Add new subject')
        print('2 - List all subjects')
        print('3 - Add new post')
        print('4 - List all posts')

        option = ask_user('Choose an option:')

        print()

        if option == '1':
            self._add_subject()
        elif option == '2':
            self._print_subjects()
        elif option == '3':
            self._add_post()
        elif option == '4':
            self._print_posts()
        else:
            print('Unkown option')

    def _menu_before_login(self):
        print('1 - Log in into existing account')
        print('2 - Create new account and log into it')

        option = ask_user('Choose an option:')

        if option == '1':
            self._perform_login()
        elif option == '2':
            self._create_user()
        else:
            print('Unkown option')

    def menu_loop(self):
        while True:
            if self._user_id:
                self._menu_after_login()
            else:
                self._menu_before_login()

            print()
            print('-' * 20)
            print()
