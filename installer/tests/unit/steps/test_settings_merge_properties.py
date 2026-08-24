"""Property-based tests for the three-way settings-merge laws (settings_merge.py).

The example tests in ``test_claude_files.py`` cover specific merge shapes; these
hypothesis properties cover the *algebraic laws* across the input space — the
oracle that the recent example-only suite lacked.

Spec-review must_fix #1: the first-install law must catch a regression that
drops user-only keys (a ``return dict(incoming)`` stub), so the load-bearing
assertion is "keys only in current survive", not just "incoming keys present".
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from installer.steps.settings_merge import merge_settings

# Scalar JSON values only at the top level: dict-valued keys merge (user-only
# subkeys are preserved), so result[k] != incoming[k] for dict keys — keeping
# values scalar lets the first-install equality be asserted exactly.
_scalars = st.one_of(st.booleans(), st.integers(), st.text(max_size=8))
_keys = st.text(min_size=1, max_size=5)
_scalar_dicts = st.dictionaries(_keys, _scalars, max_size=6)


@st.composite
def _shared_key_three_way(draw):
    """baseline/current/incoming over a shared key pool; current may diverge from baseline."""
    keys = draw(st.lists(_keys, min_size=0, max_size=6, unique=True))
    baseline = {k: draw(_scalars) for k in keys}
    current = {k: (draw(_scalars) if draw(st.booleans()) else baseline[k]) for k in keys}
    incoming = {k: draw(_scalars) for k in keys}
    return baseline, current, incoming


@given(current=_scalar_dicts, incoming=_scalar_dicts)
@settings(max_examples=200)
def test_first_install_incoming_wins_and_preserves_user_only_keys(current, incoming):
    """baseline=None: incoming wins for its keys AND user-only keys survive (clause 2 is load-bearing)."""
    result = merge_settings(None, current, incoming)
    for k, v in incoming.items():
        assert result[k] == v  # clause 1: incoming scalar value wins
    for k, v in current.items():
        if k not in incoming:
            assert result[k] == v  # clause 2: keys only in current survive — a dict(incoming) stub fails here


@given(current=_scalar_dicts, incoming=_scalar_dicts)
@settings(max_examples=200)
def test_newly_managed_setting_preserves_existing_value(current, incoming):
    """With a baseline, an existing value for a newly managed key is user-owned."""
    result = merge_settings({}, current, incoming)
    for key in current.keys() & incoming.keys():
        assert result[key] == current[key]
    for key in incoming.keys() - current.keys():
        assert result[key] == incoming[key]


@given(_shared_key_three_way())
@settings(max_examples=200)
def test_user_changed_scalar_wins_else_incoming(three_way):
    """Key in baseline∩current∩incoming: current!=baseline keeps current; current==baseline takes incoming."""
    baseline, current, incoming = three_way
    result = merge_settings(baseline, current, incoming)
    for k in baseline:
        if current[k] != baseline[k]:
            assert result[k] == current[k]  # user change wins
        else:
            assert result[k] == incoming[k]  # untouched → update to incoming


@given(current=_scalar_dicts, incoming=_scalar_dicts)
@settings(max_examples=200)
def test_reinstall_with_same_baseline_is_a_fixpoint(current, incoming):
    """Re-installing the same Pilot payload (baseline==incoming) twice is stable: f(f(x)) == f(x)."""
    once = merge_settings(incoming, current, incoming)
    twice = merge_settings(incoming, once, incoming)
    assert twice == once


@given(
    current=st.dictionaries(_keys, _scalar_dicts, max_size=4),
    incoming=st.dictionaries(_keys, _scalar_dicts, max_size=4),
)
@settings(max_examples=200)
def test_first_install_dict_field_preserves_user_only_subkeys(current, incoming):
    """For dict-valued keys present in both, user-only subkeys survive a first install."""
    result = merge_settings(None, current, incoming)
    for k, sub in current.items():
        if k in incoming:
            for subk, subv in sub.items():
                if subk not in incoming[k]:
                    assert result[k][subk] == subv
