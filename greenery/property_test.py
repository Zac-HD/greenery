import re
from hypothesis import given, note, settings, strategies as st

from greenery import lego


if __name__ == "__main__":
    raise Exception("Test files can't be run directly. Use `python -m pytest greenery`")


@st.composite
def multipliers(draw):
    lo = draw(st.integers(0, 99))
    hi = draw(st.none() | st.integers(max(1, lo), 99))
    return lego.multiplier(lego.bound(lo), lego.bound(hi))


st.register_type_strategy(
    lego.charclass,
    st.builds(
        lego.charclass,
        st.characters(blacklist_categories=("Cs",), blacklist_characters="$"),
        st.booleans(),
    ),
)
st.register_type_strategy(
    lego.bound, st.builds(lego.bound, st.none() | st.integers(0, 99))
)
st.register_type_strategy(lego.multiplier, multipliers())
st.register_type_strategy(
    lego.mult,
    st.builds(lego.mult, st.from_type(lego.charclass), st.from_type(lego.multiplier)),
)
st.register_type_strategy(
    lego.conc, st.lists(st.from_type(lego.mult)).map(lambda ls: lego.conc(*ls))
)
st.register_type_strategy(
    lego.pattern,
    st.lists(st.from_type(lego.conc), min_size=1).map(lambda ls: lego.pattern(*ls)),
)


@settings(deadline=None)
@given(st.from_type(lego.pattern))
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
