# -*- coding: utf-8 -*-
'''
    tests.utils.test_main
    ~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2014 Markus Unterwaditzer & contributors
    :license: MIT, see LICENSE for more details.
'''

import click

from click.testing import CliRunner
import pytest
import vdirsyncer.utils as utils
import vdirsyncer.doubleclick as doubleclick
from vdirsyncer.utils.vobject import split_collection

from .. import blow_up, normalize_item, SIMPLE_TEMPLATE, BARE_EVENT_TEMPLATE


class EmptyNetrc(object):
    def authenticators(self, hostname):
        return None

class EmptyKeyring(object):
    def get_password(self, *a, **kw):
        return None


@pytest.fixture(autouse=True)
def empty_password_storages(monkeypatch):
    monkeypatch.setattr('netrc.netrc', EmptyNetrc)
    monkeypatch.setattr(utils, 'keyring', EmptyKeyring())


def test_parse_options():
    o = {
        'foo': 'yes',
        'hah': 'true',
        'bar': '',
        'baz': 'whatever',
        'bam': '123',
        'asd': 'off'
    }

    a = dict(utils.parse_options(o.items()))

    expected = {
        'foo': True,
        'hah': True,
        'bar': '',
        'baz': 'whatever',
        'bam': 123,
        'asd': False
    }

    assert a == expected

    for key in a:
        # Yes, we want a very strong typecheck here, because we actually have
        # to differentiate between bool and int, and in Python 2, bool is a
        # subclass of int.
        assert type(a[key]) is type(expected[key])  # flake8: noqa


def test_get_password_from_netrc(monkeypatch):
    username = 'foouser'
    password = 'foopass'
    resource = 'http://example.com/path/to/whatever/'
    hostname = 'example.com'

    calls = []

    class Netrc(object):
        def authenticators(self, hostname):
            calls.append(hostname)
            return username, 'bogus', password

    monkeypatch.setattr('netrc.netrc', Netrc)
    monkeypatch.setattr('getpass.getpass', blow_up)

    _password = utils.get_password(username, resource)
    assert _password == password
    assert calls == [hostname]


def test_get_password_from_system_keyring(monkeypatch):
    username = 'foouser'
    password = 'foopass'
    resource = 'http://example.com/path/to/whatever/'
    hostname = 'example.com'

    class KeyringMock(object):
        def get_password(self, resource, _username):
            assert _username == username
            assert resource == utils.password_key_prefix + hostname
            return password

    monkeypatch.setattr(utils, 'keyring', KeyringMock())

    netrc_calls = []

    class Netrc(object):
        def authenticators(self, hostname):
            netrc_calls.append(hostname)
            return None

    monkeypatch.setattr('netrc.netrc', Netrc)
    monkeypatch.setattr('getpass.getpass', blow_up)

    _password = utils.get_password(username, resource)
    assert _password == password
    assert netrc_calls == [hostname]


def test_get_password_from_prompt():
    getpass_calls = []

    user = 'my_user'
    resource = 'http://example.com'

    @click.command()
    def fake_app():
        x = utils.get_password(user, resource)
        click.echo('Password is {}'.format(x))

    runner = CliRunner()
    result = runner.invoke(fake_app, input='my_password\n\n')
    assert not result.exception
    assert result.output.splitlines() == [
        'Server password for {} at host {}: '.format(user, 'example.com'),
        'Password is my_password'
    ]


def test_get_password_from_cache(monkeypatch):
    user = 'my_user'
    resource = 'http://example.com'

    @doubleclick.click.command()
    @doubleclick.click.pass_context
    def fake_app(ctx):
        ctx.obj = {}
        x = utils.get_password(user, resource)
        click.echo('Password is {}'.format(x))
        monkeypatch.setattr(doubleclick.click, 'prompt', blow_up)

        assert (user, 'example.com') in ctx.obj['passwords']
        x = utils.get_password(user, resource)
        click.echo('Password is {}'.format(x))

    runner = CliRunner()
    result = runner.invoke(fake_app, input='my_password\n')
    assert not result.exception
    assert result.output.splitlines() == [
        'Server password for {} at host {}: '.format(user, 'example.com'),
        'Save this password in the keyring? [y/N]: ',
        'Password is my_password',
        'debug: Got password for my_user from internal cache',
        'Password is my_password'
    ]



def test_get_class_init_args():
    class Foobar(object):
        def __init__(self, foo, bar, baz=None):
            pass

    all, required = utils.get_class_init_args(Foobar)
    assert all == {'foo', 'bar', 'baz'}
    assert required == {'foo', 'bar'}


def test_get_class_init_args_on_storage():
    from vdirsyncer.storage.memory import MemoryStorage

    all, required = utils.get_class_init_args(MemoryStorage)
    assert all == set(['collection', 'read_only', 'instance_name'])
    assert not required
