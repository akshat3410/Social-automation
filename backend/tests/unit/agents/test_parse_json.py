import pytest

from agents.base import AgentParseError, parse_json_response


def test_parses_plain_json():
    assert parse_json_response('{"a": 1}') == {"a": 1}


def test_parses_fenced_json():
    assert parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}


def test_parses_json_embedded_in_prose():
    assert parse_json_response('Here you go: {"a": 1} hope that helps!') == {"a": 1}


def test_parses_json_array():
    assert parse_json_response('[{"a": 1}]') == [{"a": 1}]


def test_raises_on_garbage():
    with pytest.raises(AgentParseError):
        parse_json_response("I could not produce JSON, sorry.")
