from secrets.schema import Schema, load_secrets, merge_schema
from secrets.secret import Secret
import pytest


def test_load():
    first = Schema(name='first')
    first.secrets = {
        'final': Secret(name='final', final=True, description='final'),
        'override': Secret(name='override', final=False, description='override')
    }
    data = {
        'final': 'final_value',
        'override': 'override_value'
    }
    load_secrets(first, first, data)


def test_merge_load():
    first = Schema(name='first')
    first.secrets = {
        'final': Secret(name='final', final=True, description='final'),
        'override': Secret(name='override', final=False, description='override')
    }
    first_data = {
        'final': 'final_value',
        'override': 'override_value'
    }
    second = Schema(name='second')
    second.secrets = {
        'override': Secret(name='override', final=True, description='override2'),
        'special': Secret(name='special', final=False, description='special')
    }
    second_data = {
        'override': 'override2_value',
        'special': 'special_value'
    }
    result = merge_schema(first, second)
    load_secrets(result, first, first_data)
    load_secrets(result, second, second_data)
    assert len([s for s in result.secrets.values() if s.value is None]) == 0
    assert result.secrets['override'].value == 'override2_value'
