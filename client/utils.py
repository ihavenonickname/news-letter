import re

def get_message(fault):
    match = re.match(r"<class 'Exception'>:([\w\s]+)", fault.faultString)

    return 'Server error: "{0}"'.format(match.group(1))

def ask_user(message):
    while True:
        print(message)

        answer = input()

        if re.match(r'\w', answer):
            return answer

        print('Invalid input')

def format_posts(posts):
    def format_post(post):
        mask = 'Subject: {0}\nCreation: {1}\nTitle: {2}\nBody: {3}'

        return mask.format(
            post['subject'],
            post['creation'],
            post['title'],
            post['body']
        )

    return '\n\n'.join(map(format_post, posts))
