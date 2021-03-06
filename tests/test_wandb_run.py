import pytest
import datetime
import os
import sys
import json
from .utils import git_repo

from wandb import wandb_run
from wandb import env


def get_last_val(history, key):
    val = None
    for val in history.column(key):
        pass
    return val


def test_wandb_run_args(git_repo):
    os.environ[env.ARGS] = json.dumps(["foo", "bar"])
    run = wandb_run.Run.from_environment_or_defaults()
    assert run.args == ["foo", "bar"]
    del os.environ[env.ARGS]


def test_wandb_run_args_sys(git_repo):
    sys.argv = ["rad", "cool"]
    run = wandb_run.Run.from_environment_or_defaults()
    assert run.args == ["cool"]


def test_name_and_desc_only_name(git_repo):
    os.environ[env.DESCRIPTION] = "myrunid"
    run = wandb_run.Run.from_environment_or_defaults()
    assert run.name == "myrunid"
    assert run.description == ""
    del os.environ[env.DESCRIPTION]


def test_name_and_desc(git_repo):
    os.environ[env.DESCRIPTION] = "myrunid\nmydesc"
    run = wandb_run.Run.from_environment_or_defaults()
    assert run.name == "myrunid"
    assert run.description == "mydesc"
    del os.environ[env.DESCRIPTION]


def test_name_and_desc_setters(git_repo):
    run = wandb_run.Run.from_environment_or_defaults()
    run.name = "123"
    run.description = "so much desc\nthis is fun"
    assert run.name == "123"
    assert run.description == "so much desc\nthis is fun"
    my_env = {}
    run.set_environment(my_env)
    assert my_env[env.DESCRIPTION] == "123\nso much desc\nthis is fun"


def test_history_updates_keys_until_summary_writes(git_repo):
    run = wandb_run.Run()

    run.history.add({'a': 5, 'b': 9})
    assert get_last_val(run.history, 'a') == 5
    assert get_last_val(run.history, 'b') == 9
    assert run.summary['a'] == 5
    assert run.summary['b'] == 9

    run.history.add({'a': 6, 'b': 10})
    assert get_last_val(run.history, 'a') == 6
    assert get_last_val(run.history, 'b') == 10
    assert run.summary['a'] == 6
    assert run.summary['b'] == 10

    run.summary['a'] = 112491
    assert run.summary['a'] == 112491

    run.history.add({'a': 1, 'b': 3})
    assert get_last_val(run.history, 'a') == 1
    assert get_last_val(run.history, 'b') == 3
    assert run.summary['a'] == 112491
    assert run.summary['b'] == 3

    run.history.add({'a': -40, 'b': -49})
    assert get_last_val(run.history, 'a') == -40
    assert get_last_val(run.history, 'b') == -49
    assert run.summary['a'] == 112491
    # most recent history key is logged
    assert run.summary['b'] == -49

    run.summary['c'] = 100
    assert run.summary['c'] == 100
    run.history.add({'c': 200, 'd': 300})
    assert run.summary['c'] == 100
    assert run.summary['d'] == 300

    run.history.add({'a': 1000, 'b': 2000, 'c': 200, 'd': 300})
    assert get_last_val(run.history, 'a') == 1000
    assert get_last_val(run.history, 'b') == 2000
    assert get_last_val(run.history, 'c') == 200
    assert get_last_val(run.history, 'd') == 300
    assert run.summary['a'] == 112491
    assert run.summary['b'] == 2000
    assert run.summary['c'] == 100
    assert run.summary['d'] == 300
