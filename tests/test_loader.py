from pathlib import Path

import pytest

from procurement_pattern_library.loader import (
    LoaderError,
    load_corpus,
    parse_front_matter,
)


def test_parse_front_matter_happy_path():
    text = "---\nid: foo\nname: Foo\n---\n\nbody here\n"
    fm, body = parse_front_matter(text)
    assert fm == {"id": "foo", "name": "Foo"}
    assert body.strip() == "body here"


def test_parse_front_matter_missing_fence_raises():
    with pytest.raises(LoaderError):
        parse_front_matter("no fence here at all\n")


def test_parse_front_matter_invalid_yaml_raises():
    with pytest.raises(LoaderError):
        parse_front_matter("---\nid: : :\n---\nbody\n")


def test_parse_front_matter_must_be_mapping():
    with pytest.raises(LoaderError):
        parse_front_matter("---\n- a\n- b\n---\nbody\n")


def test_load_corpus_counts(tiny_corpus: Path):
    c = load_corpus(tiny_corpus)
    assert len(c.patterns) == 3
    assert len(c.cases) == 3
    ids = {p.id for p in c.patterns}
    assert ids == {"alpha", "beta", "gamma"}


def test_load_corpus_attaches_directory_pattern_id(tiny_corpus: Path):
    c = load_corpus(tiny_corpus)
    by_path = {case.path.name: case for case in c.cases}
    assert by_path["case-1.md"].directory_pattern_id in {"alpha", "beta"}


def test_load_corpus_empty_root_is_empty(tmp_path: Path):
    c = load_corpus(tmp_path)
    assert c.patterns == []
    assert c.cases == []
