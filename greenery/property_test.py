import re
import time

from hypothesis import given, note, settings, strategies as st
import stopit

from greenery import lego


@st.composite
def multipliers(draw):
    MAX_REPEAT = 3
    lo = draw(st.integers(0, MAX_REPEAT))
    hi = draw(st.none() | st.integers(max(1, lo), MAX_REPEAT))
    return lego.multiplier(lego.bound(lo), lego.bound(hi))


CHARCLASSES = st.builds(
    lego.charclass,
    # TODO: shorthand patterns like "\d" for digit, to expose unicode issues
    st.frozensets(
        st.characters(
            blacklist_categories=("Cs",), blacklist_characters="^$", max_codepoint=127
        ),
        min_size=1,
    ),
    st.booleans(),
)
MULTS = st.builds(lego.mult, CHARCLASSES, multipliers())
CONCS = st.lists(MULTS, min_size=1, max_size=5).map(lambda ls: lego.conc(*ls))
PATTERNS = st.lists(CONCS, min_size=1, max_size=3).map(lambda ls: lego.pattern(*ls))


@settings(deadline=None)
@given(PATTERNS)
def test_roundtrip(val):
    val2 = val.reduce()
    string = str(val)
    string2 = str(val2)
    val3 = lego.parse(string2)
    note(val)
    note(val2)
    note(f"{string!r}   {string2!r}")
    note(val3)
    re.compile(string)
    re.compile(string2)


@given(PATTERNS)
def test_to_string_from_string_roundtrip(val):
    assert val == lego.parse(str(val))


@given(PATTERNS)
def test_reduce_method_is_idempotent(val):
    reduced = val.reduce()
    assert reduced == reduced.reduce()


TRIED = set()


@settings(deadline=None)
@given(PATTERNS, st.text())
def test_stdlib_equivalence(val, string):
    try:
        pattern = str(val)
        print("\n\n", repr(string), "\n", repr(val), "\n", repr(pattern), flush=True)
        re_matches = bool(re.fullmatch(pattern, string))
        with stopit.ThreadingTimeout(seconds=1, swallow_exc=True) as ctx:
            if repr(val) in TRIED:
                time.sleep(2)  # prevent flakiness
            TRIED.add(repr(val))
            le_matches = val.matches(string)
            TRIED.discard(repr(val))
        if not ctx:
            print("TIMED OUT", flush=True)
            assert ctx, ctx
        assert re_matches == le_matches
    except UnicodeError:
        pass


if __name__ == "__main__":
    test_stdlib_equivalence()
