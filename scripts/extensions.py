import re
import subprocess
import unicodedata

from jinja2.ext import Extension


def git_user_name() -> str:
    return subprocess.getoutput('git config user.name').strip()


def git_user_email() -> str:
    return subprocess.getoutput('git config user.email').strip()


def slugify(value, separator='-'):
    value = unicodedata.normalize('NFKD', str(value)).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-_\s]+', separator, value).strip('-_')

def to_camel(value):
    value = re.sub(r'[^a-zA-Z0-9\s]', '', value)
    parts = value.split()
    return parts[0].lower() + ''.join(part.title() for part in parts[1:])

class GitExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.globals['git_user_name'] = git_user_name
        environment.globals['git_user_email'] = git_user_email


class SlugifyExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters['slugify'] = slugify

class CamelCaseExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        environment.filters['to_camel'] = to_camel