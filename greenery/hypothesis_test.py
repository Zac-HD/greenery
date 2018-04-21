# -*- coding: utf-8 -*-

import string

import hypothesis.strategies as st
from hypothesis import given, assume, settings

from greenery.lego import bound, charclass, conc, mult, multiplier, \
    parse, pattern


settings.deadline = None


def st_charclass():
    return st.text(string.printable, min_size=1).map(charclass)


@st.composite
def st_mult(draw, leaf):
    m = draw(leaf)
    assume(not isinstance(m, mult))
    lo = draw(st.integers(0, 99))
    hi = draw(st.none() | st.integers(max(lo, 1), 100))
    return mult(
        m, multiplier(bound(lo), bound(hi)),
    )


def st_conc(leaf):
    return st.lists(leaf, min_size=2).map(lambda x: conc(*x))


def st_pattern(leaf):
    return st.lists(leaf, min_size=2).map(lambda x: pattern(*x))


st_any = st.deferred(lambda: (
    st_charclass() | st_mult(st_any) | st_conc(st_any) | st_pattern(st_any)
))


@given(st_any)
def test_reduces_to_fixpoint(x):
    y = x.reduce()
    assert x.reduce() == y.reduce()


@given(st_any)
def test_encode_decode(x):
    y = parse(str(x))
    assert x.reduce() == y.reduce()
