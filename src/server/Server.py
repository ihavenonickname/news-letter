import re
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from server.DataBase import DataBase

class Server():
    def __init__(self, db_name):
        self._db = DataBase(db_name, reset=False)
        self._listeners = {}

    def _is_valid_text(self, text):
        return text and re.match(r'[a-zA-Z][\w\s]*', text)

    def _dispatch_post(self, post):
        dead_ends = []

        for user_id in self._listeners:
            if post['subject'] not in self._db.get_subscriptions(user_id):
                continue

            host, port = self._listeners[user_id]

            try:
                server = ServerProxy('http://{0}:{1}'.format(host, port))
                server.notify_new_post(post)
            except Exception as ex:
                print(ex)
                dead_ends.append(user_id)

        for user_id in dead_ends:
            del self._listeners[user_id]

    def is_user_registered(self, user_id):
        if not self._is_valid_text(user_id):
            raise Exception('Invalid user identifier')

        return self._db.is_user_registered(user_id)

    def register_user(self, user_id):
        if not self._is_valid_text(user_id):
            raise Exception('Invalid address')

        if self.is_user_registered(user_id):
            raise Exception('Already registered')

        self._db.register_user(user_id)

    def add_subject(self, user_id, subject_name, posts_limit):
        if not self.is_user_registered(user_id):
            raise Exception('Uknown user')

        if not self._is_valid_text(subject_name):
            raise Exception('Invalid subject name')

        if posts_limit <= 0:
            raise Exception('Posts limit must be greater than 0')

        try:
            self._db.add_subject(subject_name, posts_limit)
        except Exception:
            raise Exception('Could not complete this operation')

    def get_subjects(self, user_id):
        if not self.is_user_registered(user_id):
            raise Exception('Uknown user')

        try:
            return list(self._db.get_subjects())
        except Exception:
            raise Exception('Could not complete this operation')

    def add_post(self, user_id, subject, title, body):
        if not self.is_user_registered(user_id):
            raise Exception('Uknown user')

        if not self._is_valid_text(subject):
            raise Exception('Invalid subject name')

        if not self._is_valid_text(title):
            raise Exception('Invalid post title')

        if not self._is_valid_text(body):
            raise Exception('Invalid post body')

        if len(body) > 180:
            raise Exception('Body is too long')

        try:
            self._db.add_post(subject, title, body)
        except Exception:
            raise Exception('Could not complete this operation')

        self._dispatch_post(self.get_last_post(subject))

    def get_all_posts(self, user_id):
        if not self.is_user_registered(user_id):
            raise Exception('Uknown user')

        posts = []

        try:
            for subject in self.get_subjects(user_id):
                for post in self._db.get_posts(subject['name']):
                    posts.append(post)
        except Exception as ex:
            raise Exception('Could not complete this operation')

        return posts

    def subscribe(self, user_id, subject):
        if not self.is_user_registered(user_id):
            raise Exception('Uknown user')

        try:
            self._db.subscribe(user_id, subject)
        except Exception:
            raise Exception('Could not complete this operation')

    def get_posts(self, subject, min_date, max_date):
        try:
            return list(self._db.get_posts(subject, min_date, max_date))
        except Exception:
            raise Exception('Could not complete this operation')

    def get_last_post(self, subject):
        try:
            return self._db.get_last_post(subject)
        except Exception:
            raise Exception('Could not complete this operation')

    def register_listener(self, user_id, host, port):
        self._listeners[user_id] = (host, port)

    def unregister_listener(self, user_id):
        del self._listeners[user_id]

    def serve(self, host, port):
        rpc_server = SimpleXMLRPCServer((host, port), allow_none=True)
        rpc_server.register_instance(self)
        rpc_server.serve_forever()
