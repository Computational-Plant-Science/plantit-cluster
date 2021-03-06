import os
from os import listdir, remove
from os.path import isdir, isfile, islink, join
import shutil
import requests


def clear_dir(dir):
    for file in listdir(dir):
        p = join(dir, file)
        if isfile(p) or islink(p):
            remove(p)
        elif isdir(p):
            shutil.rmtree(p)


def check_hello(file, name):
    assert isfile(file)
    with open(file) as file:
        lines = file.readlines()
        assert len(lines) == 1
        line = lines[0]
        assert f"Hello, {name}!" in line


token = None


class Token:
    __token = None

    @staticmethod
    def get():
        return Token.__token

    def __init__(self, token):
        Token.__token = token


def get_token():
    cyverse_username = os.environ.get('CYVERSE_USERNAME', None)
    cyverse_password = os.environ.get('CYVERSE_PASSWORD', None)

    if cyverse_username is None:
        raise ValueError("Missing environment variable 'CYVERSE_USERNAME'")
    if cyverse_password is None:
        raise ValueError("Missing environment variable 'CYVERSE_PASSWORD'")

    if Token.get() is None:
        response = requests.get(
            'https://de.cyverse.org/terrain/token/cas',
            auth=(cyverse_username, cyverse_password)).json()
        Token(response['access_token'])

    return Token.get()