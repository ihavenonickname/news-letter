import sqlite3
import contextlib
from datetime import datetime
from os import remove

class DataBase():
    def __init__(self, database_name, reset=False):
        self._database_name = database_name

        if reset:
            with contextlib.suppress(FileNotFoundError):
                remove(self._database_name)

        self._create_tables()

    def _execute_query(self, query, *args):
        with sqlite3.connect(self._database_name) as conn:
            conn.cursor().execute(query, args)
            conn.commit()

    def _execute_select(self, query, *args):
        with sqlite3.connect(self._database_name) as conn:
            yield from conn.cursor().execute(query, args)

    def _create_tables(self):
        self._execute_query('''
        create table if not exists subjects (
            name text primary key,
            posts_limit integer not null
        )''')

        self._execute_query('''
        create table if not exists posts (
            id integer primary key,
            subject_name name references subjects (name),
            title text not null,
            body text not null,
            creation timestamp not null
        )''')

        self._execute_query('''
        create table if not exists users (
            id text primary key
        )
        ''')

        self._execute_query('''
        create table if not exists subscriptions (
            subject_name name references subjects (name),
            user_id id references users (id)
        )
        ''')

    def add_subject(self, name, posts_limit):
        query = '''
        insert into subjects
        (name, posts_limit)
        values (?, ?)
        '''

        self._execute_query(query, name, posts_limit)

    def get_subjects(self):
        query = 'select name, posts_limit from subjects'

        for name, posts_limit in self._execute_select(query):
            yield {
                'name': name,
                'posts_limit': posts_limit
            }

    def add_post(self, subject, title, body):
        query = '''
        insert into posts
        (subject_name, title, body, creation)
        values (?, ?, ?, ?)
        '''

        self._execute_query(query, subject, title, body, datetime.now())

        query = '''
        select posts_limit
        from subjects
        where name = ?
        '''

        offset = int(next(self._execute_select(query, subject))[0])

        query = '''
        select p.id
        from posts as p
        join subjects as s on s.name = p.subject_name
        where s.name = ?
        order by creation desc
        limit -1
        offset ?
        '''

        post_ids = [x for x, in self._execute_select(query, subject, offset)]

        if post_ids:
            ids = ','.join(map(str, post_ids))
            self._execute_query('delete from posts where id in ({0})'.format(ids))

    def get_posts(self, subject, min_date=None, max_date=None):
        if not min_date:
            min_date = datetime(year=1999, month=1, day=1)

        if not max_date:
            max_date = datetime.now()

        query = '''
        select subject_name, title, body, creation
        from posts
        where subject_name = ? and creation between ? and ?
        '''

        posts = self._execute_select(query, subject, min_date, max_date)

        for subject, title, body, creation in posts:
            yield {
                'subject': subject,
                'title': title,
                'body': body,
                'creation': creation
            }

    def get_last_post(self, subject):
        query = '''
        select subject_name, title, body, creation
        from posts
        where subject_name = ?
        order by creation desc
        limit 1
        '''

        try:
            post = next(self._execute_select(query, subject))
        except Exception:
            return None

        subject, title, body, creation = post

        return {
            'subject': subject,
            'title': title,
            'body': body,
            'creation': (creation)
        }

    def register_user(self, user_id):
        query = '''
        insert into users
        (id)
        values (?)
        '''

        self._execute_query(query, user_id)

    def is_user_registered(self, user_id):
        query = '''
        select id
        from users
        where id = ?
        '''

        return any(self._execute_select(query, user_id))

    def subscribe(self, user_id, subject):
        query = '''
        insert into subscriptions
        (user_id, subject_name)
        values (?, ?)
        '''

        self._execute_query(query, user_id, subject)

    def get_subscriptions(self, user_id):
        query = '''
        select subject_name
        from subscriptions
        where user_id = ?
        '''

        for subject, in self._execute_select(query, user_id):
            yield subject
