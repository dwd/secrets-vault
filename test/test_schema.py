from secrets.schema import Schema, merge_schema
from secrets.secret import Secret


def test_merge():
    first = Schema()
    second = Schema()
    result = merge_schema(first, second)
    assert isinstance(result, Schema)


def test_merge_secrets():
    first = Schema(name='first')
    first.secrets = {
        'final': Secret(name='final', final=True, description='final'),
        'override': Secret(name='override', final=False, description='override')
    }
    second = Schema(name='second')
    second.secrets = {
        'override': Secret(name='override', final=True, description='override2'),
        'special': Secret(name='special', final=False, description='special')
    }
    result = merge_schema(first, second)
    assert isinstance(result, Schema)
    assert result.name == 'second'
    assert len(result.secrets) == 3
    assert result.secrets['final'].source == 'first'
    assert result.secrets['override'].source == 'second'
    assert result.secrets['special'].source == 'second'

