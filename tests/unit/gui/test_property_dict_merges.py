import pytest

from arcade.gui import DictProperty, bind


class DictHolder:
    values = DictProperty()


def observe(holder):
    notifications = []

    def changed(instance, value, old_value):
        notifications.append((id(instance), dict(value), dict(old_value)))

    bind(holder, "values", changed)
    return notifications


@pytest.mark.parametrize(
    ("args", "kwargs", "updates"),
    [
        ((), {"score": 2}, {"score": 2}),
        (({"score": 2},), {"overlap": 3}, {"score": 2, "overlap": 3}),
        (
            ([("score", 2), ("overlap", 3)],),
            {"overlap": 4},
            {"score": 2, "overlap": 4},
        ),
        ((), {"self": 2}, {"self": 2}),
        ((), {"args": 2, "kwargs": 3}, {"args": 2, "kwargs": 3}),
        (({"score": 2},), {}, {"score": 2}),
        ((), {}, {}),
    ],
)
def test_update_accepts_dict_merge_forms_and_notifies_once(args, kwargs, updates):
    holder = DictHolder()
    original = {"existing": 1, "overlap": 0}
    holder.values = original
    alias = holder.values
    notifications = observe(holder)

    result = holder.values.update(*args, **kwargs)

    expected = {**original, **updates}
    assert result is None
    assert holder.values is alias
    assert holder.values == expected
    assert notifications == [(id(holder), expected, original)]
    assert original == {"existing": 1, "overlap": 0}


@pytest.mark.parametrize("through_property", [False, True])
@pytest.mark.parametrize("source_type", [dict, list, iter])
def test_inplace_union_preserves_identity_and_notifies_once(through_property, source_type):
    holder = DictHolder()
    original = {"existing": 1, "overlap": 0}
    holder.values = original
    alias = holder.values
    notifications = observe(holder)
    source = source_type([("score", 2), ("existing", 5)])

    if through_property:
        holder.values |= source
    else:
        alias |= source

    expected = {"existing": 5, "overlap": 0, "score": 2}
    assert holder.values is alias
    assert holder.values == expected
    assert notifications == [(id(holder), expected, original)]
    assert original == {"existing": 1, "overlap": 0}


def test_nonmutating_union_does_not_notify():
    holder = DictHolder()
    holder.values = {"existing": 1}
    notifications = observe(holder)

    right = holder.values | {"score": 2}
    left = {"score": 2} | holder.values

    assert right == left == {"existing": 1, "score": 2}
    assert type(right) is type(left) is dict
    assert holder.values == {"existing": 1}
    assert notifications == []


def test_invalid_update_does_not_change_or_notify():
    holder = DictHolder()
    holder.values = {"existing": 1}
    notifications = observe(holder)

    with pytest.raises(TypeError):
        holder.values.update(object(), score=2)

    assert holder.values == {"existing": 1}
    assert notifications == []
