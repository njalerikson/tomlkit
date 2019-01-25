# -*- coding: utf-8 -*-
from collections.abc import MutableSequence, Sequence, Mapping
from ..exceptions import MixedArrayTypesError
from ._utils import pyobj, flatten
from ._hidden import _Hidden, Comment, Newline
from ._trivia import _Value, _Container, _TriviaMeta
from ._key import _Key


class _Link(object):
    # the individual links that remembers the insert order but also keeps track
    # of the hidden comments
    __slots__ = ["key", "value", "scope", "__weakref__"]

    def __hash__(self):
        try:
            if self.key is not None:
                return hash(self.key)
        except AttributeError:
            pass

        raise TypeError("unhashable type: '{}'".format(self.__class__.__name__))

    def __repr__(self):
        try:
            if self.key is not None:
                tmp = self.key
            else:
                raise ValueError
        except (AttributeError, ValueError):
            try:
                tmp = self.value
            except AttributeError:
                tmp = "missing key/value"

        return "<{} {!r}>".format(self.__class__.__name__, tmp)


class _Links(list):
    __slots__ = ["_map"]

    def __init__(self):
        self._map = {}

    def __getitem__(self, key):
        if isinstance(key, int):
            # return the link given the index
            return super(_Links, self).__getitem__(key)

        # return the link given the key
        return self._map[key]

    def __delitem__(self, key):
        if isinstance(key, int):
            # delete the link by the index
            link = self[key]
            super(_Links, self).__delitem__(key)
            # delete from map if the link has a key
            if link.key:
                del self._map[link.key]
            return

        # delete the link by the key
        link = self._map.pop(key)
        super(_Links, self).remove(link)

    def insert(self, index, link):
        assert isinstance(index, int)
        assert isinstance(link, _Link)
        if link.key:
            if link.key in self._map:
                raise KeyError("Cannot insert multiple links with the same key")
            self._map[link.key] = link
        super(_Links, self).insert(index, link)

    def __contains__(self, item):
        if isinstance(item, _Link):
            return super(_Links, self).__contains__(item)
        return item in self._map

    def clear(self):
        while self:
            self.pop()

    append = MutableSequence.append
    reverse = MutableSequence.reverse
    extend = MutableSequence.extend
    pop = MutableSequence.pop
    remove = MutableSequence.remove
    __iadd__ = MutableSequence.__iadd__

    def __setitem__(self, *args, **kwargs):
        raise NotImplementedError("Cannot set link")

    def sort(self, *args, **kwargs):
        raise NotImplementedError("Cannot sort links")

    def copy(self):
        raise NotImplementedError("Cannot copy links")


class Comments(list):
    __slots__ = ["_links", "_nl"]

    def __init__(self, links=None, nl=True):
        self._links = _Links() if links is None else links
        self._nl = bool(nl)

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise ValueError("comment slicing not allowed")

        link = self._links[index]

        if link.key is not None:
            raise IndexError("Cannot get {}".format(index))

        return link.value

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise ValueError("comment slicing not allowed")

        link = self._links[index]

        if link.key is not None:
            raise IndexError("Cannot set {}".format(index))

        if not self._nl and isinstance(value, Newline):
            raise ValueError("Cannot set newlines")
        elif not isinstance(value, _Hidden):
            value = Comment(value)
        link.value = value

    def __delitem__(self, index):
        if isinstance(index, slice):
            raise ValueError("comment slicing not allowed")

        link = self._links[index]

        if link.key is not None:
            raise IndexError("Cannot delete {} (not a comment value)".format(index))

        del self._links[index]

    def __len__(self):
        # number of comments is the number of links - number of keys
        return len(self._links) - len(self._links._map)

    def __bool__(self):
        return len(self) > 0

    def __iter__(self):
        for link in self._links:
            if link.key is None:
                yield link.value

    def __repr__(self):
        return "{{{}}}".format(
            ", ".join(
                "{}: {!r}".format(i, link.value)
                for i, link in enumerate(self._links)
                if link.key is None
            )
        )

    __str__ = __repr__

    def pop(self, index=None):
        if len(self) == 0:
            raise IndexError("pop from empty list")

        if index is None:
            index = len(self._links) - 1
            while index >= 0:
                link = self._links[index]
                if link.key is None:
                    del self._links[index]
                    return link.value
                index -= 1
        else:
            link = self._links[index]
            if link.key is None:
                del self._links[index]
                return link.value

        raise IndexError("Cannot pop {}".format(index))

    def insert(self, index, value):
        link = _Link()
        link.key = None
        if not self._nl and isinstance(value, Newline):
            raise ValueError("Cannot set newlines")
        elif not isinstance(value, _Hidden):
            value = Comment(value)
        link.value = value

        self._links.insert(index, link)

    def append(self, value):
        self.insert(len(self._links), value)


class _KVSMMeta(_TriviaMeta):
    def key():
        def fget(self):
            return self._key

        def fset(self, value):
            if not issubclass(value, _Key):
                raise TypeError("key must be a _Key, not {!r}".format(value))
            self._key = value

        return locals()

    key = property(**key())

    def values():
        def fget(self):
            try:
                return self._values
            except AttributeError:
                return ()

        def fset(self, value):
            value = tuple(value)
            if not all(issubclass(v, _Value) for v in value):
                raise TypeError(
                    "values must be an iterable of _Value, not {!r}".format(value)
                )
            self._values = value

        return locals()

    values = property(**values())

    def sequence():
        def fget(self):
            try:
                return self._sequence
            except AttributeError:
                return None

        def fset(self, value):
            if not (issubclass(value, _Container) and issubclass(value, Sequence)):
                raise TypeError(
                    "sequence must be a Sequence/_Container, not {!r}".format(value)
                )
            self._sequence = value

        return locals()

    sequence = property(**sequence())

    def mapping():
        def fget(self):
            try:
                return self._mapping
            except AttributeError:
                return None

        def fset(self, value):
            if not (issubclass(value, _Container) and issubclass(value, Mapping)):
                raise TypeError(
                    "mapping must be a Mapping/_Container, not {!r}".format(value)
                )
            self._mapping = value

        return locals()

    mapping = property(**mapping())


class _KVSM(_Container, metaclass=_KVSMMeta):
    def __new__(cls, value=None, parent=None, handle=None):
        if isinstance(value, cls):
            return value, False

        self = super(_KVSM, cls).__new__(cls)

        if parent is None:
            parent = self
        else:
            assert isinstance(parent, _Container)
        self._parent = parent
        if handle is None:
            handle = _Link()
            handle.key = ()
            handle.value = None
            handle.scope = None
        else:
            assert isinstance(handle, _Link)
        self._handle = handle

        self._value_map = {}

        self._links = _Links()
        self._comments = Comments(links=self._links)

        return self, True

    def __init__(self, value=None, parent=None, handle=None):
        pass


class _Table(_KVSM, dict):
    pass


class _Array(_KVSM, list):
    pass


class TableFactory:
    def __new__(cls):
        class Table(_Table):
            # self[key] = link
            # self._value_map[link] = value
            # link.key = (*self._handle.key, key)
            # link.value = self
            # link.scope = scope
            # link in scope._links

            __inline_count__ = 3

            def __new__(cls, value=None, parent=None, handle=None):
                self, new = super(Table, cls).__new__(cls, value, parent, handle)

                self._head_comments = Comments(nl=False)

                if new and value:
                    self.update(value)

                return self

            @property
            def root(self):
                try:
                    return self._root
                except AttributeError:
                    if self._parent is self:
                        self._root = self
                        return self._root
                    self._root = self._parent.root
                    return self._root

            @property
            def head_comments(self):  # type: () -> HeadComments
                return self._head_comments

            @property
            def comments(self):  # type: () -> Comments
                return self._comments

            @property
            def _derived_complexity(self):
                # a table has a derived complexity if:
                #      there are comments
                #   or it has more than __inline_count__ values
                #   or any of the values are complex
                return bool(
                    self._comments
                    or len(self) > self.__inline_count__
                    or any(v.complexity for v in self.values())
                )

            @property
            def _complexity(self):
                # a table has a base complexity if:
                #      the _complex value is set
                #   or if self if root
                #   or self has a derived complexity
                try:
                    return self._complex
                except AttributeError:
                    pass

                # if self is the root then we remember that as perpetually complex
                if self.root is self:
                    self._complex = True
                    return self._complex

                return self._derived_complexity

            def complexity():
                def fget(self):
                    # a table is considered complex if:
                    #      self has a base complexity
                    #   or (
                    #           parent is sequence
                    #       and any of the other siblings' have a base complexity
                    #   )

                    return bool(
                        self._complexity
                        or (
                            isinstance(self._parent, self.__class__.sequence)
                            and (
                                (
                                    hasattr(self._parent, "_complex")
                                    and self._parent._complex
                                )
                                or any(
                                    v._complexity for v in self._parent if v is not self
                                )
                            )
                        )
                    )

                def fset(self, value):
                    if value is None:
                        return

                    value = bool(value)
                    if value is not True:
                        raise ValueError(
                            "Cannot set complexity to False, complexity state can only be set "
                            "to True OR deleted."
                        )
                    self._complex = value

                def fdel(self):
                    del self._complex

                return locals()

            complexity = property(**complexity())

            def explicit():
                def fget(self):
                    try:
                        return self._explicit
                    except AttributeError:
                        pass

                    # AoT is always explicit
                    if isinstance(self._parent, self.__class__.sequence):
                        self._explicit = True
                        return self._explicit

                    return False

                def fset(self, value):
                    if value is None:
                        return

                    value = bool(value)
                    if value is not True:
                        raise ValueError(
                            "Cannot set explicitness to False, explicit state can only be set "
                            "to True."
                        )
                    self._explicit = value

                return locals()

            explicit = property(**explicit())

            def _getitem(self, key, **kwargs):
                rkey = ()
                if isinstance(key, tuple):
                    key, *rkey = key
                    rkey = tuple(rkey)

                try:
                    link = super(Table, self).__getitem__(key)
                except KeyError:
                    if "default" in kwargs:
                        return (None,), kwargs["default"]
                    raise

                value = self._value_map[link]

                if rkey:
                    rkey, value = value._getitem(rkey, **kwargs)
                    return (link.key[-1], *rkey), value
                return (link.key[-1],), value

            def __getitem__(self, key, infer=False):
                return self._getitem(key, infer=infer)[1]

            def getitem(self, key, default=None, infer=False):
                key, value = self._getitem(key, default=default, infer=infer)
                if len(key) > 1:
                    return key, value
                return key[0], value

            def get(self, key, default=None, infer=False):
                return self._getitem(key, default=default, infer=infer)[1]

            def setdefault(self, key, value, infer=False):
                try:
                    return self.__getitem__(key, infer=infer)
                except KeyError:
                    self.__setitem__(key, value, infer=infer)
                    return self.__getitem__(key, infer=infer)

            def __setitem__(self, key, value, scope=None, infer=False):
                if isinstance(key, tuple):
                    key, *rkey = key
                    if rkey:
                        rkey = tuple(rkey)
                        container = self.setdefault(key, {}, infer=infer)
                        scope = self if scope is None else scope
                        return container.__setitem__(rkey, value, scope, infer=infer)

                try:
                    # this key has been set before, no need to insert a new link
                    link = super(Table, self).__getitem__(key)

                    ovalue = self._value_map[link]
                    if value is ovalue:
                        # already set
                        return

                    if isinstance(ovalue, _Container):
                        # this is a nested container
                        ovalue.clear()

                    # update value
                    self._set_value(link, value)
                except KeyError:
                    # this is a new key, inserting a new link
                    link = _Link()
                    link.key = (*self._handle.key, self.__class__.key(key))
                    link.value = self

                    self._add_link(link, value, scope)

                    # set link at key
                    super(Table, self).__setitem__(link.key[-1], link)

            def _set_value(self, link, value, insert_link=lambda _: None):
                type = None
                if isinstance(value, tuple):
                    type, value = value

                # process value as mapping if the type is mapping OR the value is a Mapping
                if (
                    self.__class__.mapping
                    and type is self.__class__.mapping
                    or isinstance(value, Mapping)
                ):
                    insert_link(True)
                    value = self.__class__.mapping(
                        value=value, parent=self, handle=link
                    )

                # process value as sequence if the type is sequence OR the value is a Sequence
                elif (
                    self.__class__.sequence
                    and type is self.__class__.sequence
                    or (
                        isinstance(value, Sequence)
                        and not isinstance(value, (str, tuple))
                    )
                ):
                    insert_link(True)
                    value = self.__class__.sequence(
                        value=value, parent=self, handle=link
                    )

                # use the provided type to process value
                elif type:
                    if not issubclass(type, _Value):
                        raise TypeError(
                            "Cannot convert {} to valid types ({})".format(
                                value,
                                ", ".join(v.__name__ for v in self.__class__.values),
                            )
                        )

                    insert_link(False)
                    value = type(value)

                # this is a normal value, process using the value types
                else:
                    insert_link(False)
                    for type in self.__class__.values:
                        try:
                            value = type(value)
                            break
                        except TypeError:
                            pass

                    if not isinstance(value, self.__class__.values):
                        err = "Cannot convert {} to valid types ({})".format(
                            value, ", ".join(t.__name__ for t in self.__class__.values)
                        )
                        raise TypeError(err)

                # set value at link
                self._value_map[link] = value

            def _add_link(self, link, value, scope):
                def insert_link(scope, is_container):
                    # this is every item's "original" inline scope
                    scope = self if scope is None else scope
                    link.scope = scope

                    # store a link into scope such that we can render in the correct order
                    scope._links.append(link)

                    # containers store a second link into the root in case the container
                    # needs to be rendered as a complex structure
                    if is_container and scope is not self.root:
                        self.root._links.append(link)

                self._set_value(
                    link, value, lambda is_container: insert_link(scope, is_container)
                )

            def update(self, *args, **kwargs):
                if len(args) > 1:
                    raise TypeError(
                        "update expected at most 1 arguments, got {}".format(len(args))
                    )

                if args:
                    arg = args[0]
                    if isinstance(arg, _Table):
                        for link in arg._links:
                            if link.key is None:
                                self._comments.append(link.value)
                            else:
                                self[link.key] = arg[link.key]
                    elif isinstance(arg, Mapping):
                        for key in arg:
                            self[key] = arg[key]
                    elif hasattr(arg, "keys"):
                        for key in arg.keys():
                            self[key] = arg[key]
                    else:
                        for key, value in arg:
                            if key is None:
                                self._comments.append(value)
                            else:
                                self[key] = value

                for key, value in kwargs.items():
                    self[key] = value

            def pop(self, *args, _return=True):
                if len(args) == 0:
                    raise TypeError("pop expected at least 1 arguments, got 0")
                elif len(args) > 2:
                    raise TypeError(
                        "pop expected at most 2 arguments, got {}".format(len(args))
                    )

                key = args[0]
                args = args[1:]

                try:
                    link = super(Table, self).pop(key)
                except KeyError:
                    if args:
                        return args[0]
                    raise

                # remove value from mapping
                value = self._value_map.pop(link)
                tmp = pyobj(value) if _return else None

                # remove the link from scope and root
                del link.scope._links[link.key]
                try:
                    del self.root._links[link.key]
                except KeyError:
                    pass

                if isinstance(value, _Container):
                    # this is a nested container
                    value.clear()

                return tmp

            def popitem(self):
                key, link = super(Table, self).popitem()

                # remove value from mapping
                value = self._value_map.pop(link)
                tmp = pyobj(value)

                # remove the link from scope and root
                del link.scope._links[link.key]
                try:
                    del self.root._links[link.key]
                except KeyError:
                    pass

                if isinstance(value, _Container):
                    # this is a nested container
                    value.clear()

                return key, tmp

            def clear(self):
                while self:
                    self.popitem()

            def __delitem__(self, key):
                if isinstance(key, tuple):
                    del self.__getitem__(key[:-1])[key[-1]]
                    return

                self.pop(key, _return=False)

            def items(self):
                for k in self:
                    yield k, self[k]

            def keys(self):
                for k in self:
                    yield k

            def values(self):
                for k in self:
                    yield self[k]

            def __contains__(self, key):
                rkey = ()
                if isinstance(key, tuple):
                    key, *rkey = key
                    rkey = tuple(rkey)

                if super(Table, self).__contains__(key):
                    if rkey:
                        return rkey in self[key]
                    return True
                return False

            def __eq__(self, other):
                if not isinstance(other, Mapping):
                    return False

                if len(other) != len(self):
                    return False

                return all(self[k] == other[k] for k in self)

            def __flatten__(self):
                is_root = self.root is self
                prelen = len(self._handle.key)
                inline = not self.complexity

                simp = []
                comp = []

                # if this the root and it has a comment then we want to insert its
                # comment at the top
                if is_root:
                    simp.extend(map(flatten, self.head_comments))
                    if self.comment:
                        simp.append(flatten(self.comment))

                for link in self._links:
                    if link.key is None:
                        # this is a hidden link
                        simp.append(flatten(link.value))
                    else:
                        # this is a normal key-value link

                        # fetch and flatten key
                        key = []
                        for k in link.key[prelen:]:
                            key.extend(k.__flatten__())
                        key = ".".join(key)

                        # fetch value
                        value = link.value._value_map[link]

                        # flatten value
                        if value.complexity:
                            if isinstance(value, Mapping):
                                if is_root:
                                    # this is a Table or AoT

                                    # fixup key as Table
                                    key = "[{}]".format(key)

                                    # if this table is inside of an Array it's an AoT
                                    if isinstance(value._parent, Sequence):
                                        key = "[{}]".format(key)

                                    # comments are applied directly to the key
                                    key = value.comment.apply(key)

                                    # insert the key and the flattened value
                                    tmp = value.__flatten__()
                                    if value.explicit or tmp:
                                        comp.extend(map(flatten, value.head_comments))
                                        comp.append(key)
                                        comp.extend(tmp or [""])
                                continue
                            elif isinstance(value, Sequence):
                                # the complex array itself is not displayed, the individual
                                # Tables have already been linked into root so they will be
                                # displayed there
                                continue

                        if link.scope is self:
                            tmp = flatten(value)
                            if tmp:
                                if inline:
                                    tmp += ","
                                tmp = value.comment.apply(tmp)
                                simp.append("{} = {}".format(key, tmp))

                if inline:
                    if simp:
                        # remove trailing comma when inline
                        simp[-1] = simp[-1][:-1]
                    if self.explicit or simp:
                        # this is an inline table, join with commas and style with {}
                        return ["{" + " ".join(simp) + "}"]
                    return []
                if simp and comp:
                    # we have both, put a newline between them
                    return simp + [""] + comp
                # return the one that has stuff
                if simp:
                    return simp + [""]
                return comp

            def __repr__(self):
                return (
                    "{"
                    + ", ".join("{!r}: {!r}".format(*kv) for kv in self.items())
                    + "}"
                )

            def __pyobj__(self):  # type: () -> dict
                return {
                    key.__pyobj__(): value.__pyobj__() for key, value in self.items()
                }

            def __hiddenobj__(self):
                is_root = self.root is self
                prelen = len(self._handle.key)
                tmp = []
                for link in self._links:
                    if link.key is None:
                        key = None
                        value = link.value
                    else:
                        if is_root and link.scope is not self:
                            continue
                        key = link.key[prelen:]
                        value = link.value._value_map[link]
                        if isinstance(value, _Container):
                            value = value.__hiddenobj__()
                    tmp.append((key, value))
                return (Table, tmp)

            def _getstate(self, protocol=3):
                return (self.__hiddenobj__()[1],)

        return Table


class ArrayFactory:
    def __new__(cls):
        class Array(_Array):
            # self[index] = link
            # self._value_map[link] = value
            # link.key = (*self._handle.key, hiddenkey)
            # link.value = self
            # link.scope = scope
            # link in scope._links

            __inline_count__ = 3
            __indent__ = " " * 4

            def __new__(cls, value=None, parent=None, handle=None):
                self, new = super(Array, cls).__new__(cls, value, parent, handle)

                if new and value:
                    self.extend(value)

                return self

            @property
            def root(self):
                try:
                    return self._root
                except AttributeError:
                    if self._parent is self:
                        self._root = self
                        return self._root
                    self._root = self._parent.root
                    return self._root

            @property
            def _lvl(self):
                if self._parent is self:
                    return 0
                return self._parent._lvl + 1

            @property
            def comments(self):  # type: () -> Comments
                return self._comments

            @property
            def type(self):
                # if an array is predesignated as complex, then its type is automatically Table
                try:
                    if self._complex:
                        return self.__class__.mapping
                except AttributeError:
                    pass

                # return the type if this Array has previously had a type
                try:
                    return self._type
                except AttributeError:
                    pass

                # if this Array hasn't previously had a type, check to see if it does now
                try:
                    self._type = type(self[0])
                    return self._type
                except IndexError:
                    pass

                # this Array has no type yet
                return None

            @property
            def _derived_complexity(self):
                # an array has a derived complexity if:
                #       its type is Table
                #   and any of the tables are complex
                return bool(
                    self.type == self.__class__.mapping
                    and any(t.complexity for t in self)
                )

            @property
            def _complexity(self):
                # an array has a base complexity if:
                #      the _complex value is set
                #   or self has a derived complexity
                try:
                    return self._complex
                except AttributeError:
                    pass

                return self._derived_complexity

            def complexity():
                def fget(self):
                    # an array is considered complex if:
                    #   self has a base complexity
                    return self._complexity

                def fset(self, value):
                    if value is None:
                        return

                    value = bool(value)
                    if value is not True:
                        raise ValueError(
                            "Cannot set complexity to False, complexity state can only be set "
                            "to True OR deleted."
                        )
                    if self.type not in (self.__class__.mapping, None):
                        raise ValueError("Cannot change complexity of a inline array.")
                    self._complex = value

                def fdel(self):
                    del self._complex

                return locals()

            complexity = property(**complexity())

            def __getitem__(self, index, infer=False):
                if isinstance(index, slice):
                    return [self[i] for i in range(index.start, index.stop, index.step)]

                rindex = ()
                if isinstance(index, tuple):
                    index, *rindex = index
                    rindex = tuple(rindex)

                if infer and not isinstance(index, int):
                    rindex = (index, *rindex)
                    index = -1

                link = super(Array, self).__getitem__(index)
                value = self._value_map[link]

                if rindex:
                    return value.__getitem__(rindex, infer=infer)
                return value

            # allow scope to be passed in, just don't use it
            def __setitem__(self, index, value, scope=None, infer=False):
                if isinstance(index, tuple):
                    index, *rindex = index
                    if rindex:
                        rindex = tuple(rindex)
                        container = self.__getitem__(index, infer=infer)
                        return container.__setitem__(rindex, value, infer=infer)

                if (infer and not isinstance(index, int)) or isinstance(
                    index, self.__class__.key
                ):
                    if not isinstance(index, self.__class__.key):
                        rindex = (index, *rindex)
                    index = -1
                    container = self.__getitem__(index, infer=infer)
                    return container.__setitem__(rindex, value, infer=infer)

                # can only set an index that already exists, no need to insert a new link
                link = super(Array, self).__getitem__(index)

                ovalue = self._value_map[link]
                if value is ovalue:
                    # already set
                    return

                if isinstance(ovalue, _Container):
                    # this is a nested container
                    ovalue.clear()

                # update value
                self._set_value(link, value)

            def insert(self, index, value):
                link = _Link()
                link.key = (*self._handle.key, self.__class__.key())
                link.value = self

                self._add_link(index, link, value)

                # set link at index
                super(Array, self).insert(index, link)

            def _set_value(self, link, value, insert_link=lambda _: None):
                type = None
                if isinstance(value, tuple):
                    type, value = value

                # process value as mapping if the type is mapping OR the value is a Mapping
                if (
                    self.__class__.mapping
                    and type is self.__class__.mapping
                    or (
                        isinstance(value, Mapping)
                        and self.type in (None, self.__class__.mapping)
                    )
                ):
                    insert_link(True)
                    value = self.__class__.mapping(
                        value=value, parent=self, handle=link
                    )

                # process value as sequence if the type is sequence OR the value is a Sequence
                elif (
                    self.__class__.sequence
                    and type is self.__class__.sequence
                    or (
                        isinstance(value, Sequence)
                        and not isinstance(value, (str, tuple))
                        and self.type in (None, self.__class__.sequence)
                    )
                ):
                    insert_link(True)
                    value = self.__class__.sequence(
                        value=value, parent=self, handle=link
                    )

                # use the provided type to process value
                elif type:
                    if self.type and type is not self.type:
                        raise MixedArrayTypesError

                    if not issubclass(type, _Value):
                        raise TypeError(
                            "Cannot convert {} to valid types ({})".format(
                                value,
                                ", ".join(s.__name__ for s in self.__class__.values),
                            )
                        )

                    insert_link(False)
                    value = type(value)

                # this is a normal value, process using the value types
                else:
                    insert_link(False)
                    for type in self.__class__.values:
                        try:
                            value = type(value)
                            break
                        except TypeError:
                            pass

                    if self.type and not isinstance(value, self.type):
                        raise MixedArrayTypesError

                    if not isinstance(value, self.__class__.values):
                        err = "Cannot convert {} to valid types ({})".format(
                            value, ", ".join(t.__name__ for t in self.__class__.values)
                        )
                        raise TypeError(err)

                # set value at link
                self._value_map[link] = value

            def _add_link(self, index, link, value):
                def insert_link(is_container):
                    nonlocal index

                    # this is every containers "original" inline scope
                    scope = self
                    link.scope = scope

                    # store a link into scope/root such that we can render in the correct order
                    try:
                        # retrieve the link currently stored at this index, this will allow us
                        # to fetch the link index
                        olink = super(Array, self).__getitem__(index)
                    except IndexError:
                        # unable to fetch an existing location, the provided index is out of
                        # bounds
                        if index > 0:
                            # past end of list, append
                            scope._links.append(link)
                            if is_container and scope is not self.root:
                                self.root._links.append(link)
                            return

                        try:
                            olink = super(Array, self).__getitem__(0)
                        except IndexError:
                            # first link, append
                            scope._links.append(link)
                            if is_container and scope is not self.root:
                                self.root._links.append(link)
                            return

                    # get link index of the old link and insert new link at that location
                    index = scope._links.index(olink)
                    scope._links.insert(index, link)

                    # insert new link at old link index in the root links
                    if is_container and scope is not self.root:
                        index = self.root._links.index(olink)
                        self.root._links.insert(index, link)

                self._set_value(link, value, insert_link)

            def extend(self, *args):
                if len(args) > 1:
                    raise TypeError(
                        "extend expected at most 1 arguments, got {}".format(len(args))
                    )

                if args:
                    arg = args[0]
                    if isinstance(arg, Array):
                        i = 0
                        for link in arg._links:
                            if link.key is None:
                                self._comments.append(link.value)
                            else:
                                self.append(arg[i])
                                i += 1
                    else:
                        for value in arg:
                            if isinstance(value, _Hidden):
                                self._comments.append(value)
                            else:
                                self.append(value)

            def append(self, value):
                self.insert(len(self), value)

            def pop(self, *args, _return=True):
                if len(args) == 0:
                    args = (-1,)
                elif len(args) > 1:
                    raise TypeError(
                        "pop expected at most 1 argument, got {}".format(len(args))
                    )

                index = args[0]

                link = super(Array, self).pop(index)

                # remove value from mapping
                value = self._value_map.pop(link)
                tmp = pyobj(value) if _return else None

                # remove the link from the scope and root
                del link.scope._links[link.key]
                try:
                    del self.root._links[link.key]
                except KeyError:
                    pass

                if isinstance(value, _Container):
                    # this is a nested container
                    value.clear()

                return tmp

            def clear(self):
                while self:
                    self.pop()

            def __delitem__(self, index):
                if isinstance(index, tuple):
                    del self.__getitem__(index[:-1])[index[-1]]
                    return

                self.pop(index, _return=False)

            def __iter__(self):
                for i in range(len(self)):
                    yield self[i]

            def __eq__(self, other):
                if not isinstance(other, Sequence) or isinstance(other, str):
                    return False

                if len(other) != len(self):
                    return False

                return all(s == o for s, o in zip(self, other))

            def __add__(self, other):
                return pyobj(self) + other

            def __iadd__(self, other):
                if not isinstance(other, Sequence) or isinstance(other, str):
                    raise TypeError(
                        "can only concatenate list (not {}) to list".foramt(type(other))
                    )

                self.extend(other)
                return self

            def __flatten__(self):  # type: () -> str
                # this Array is complex, we ignore it
                if self.complexity:
                    return []

                has_comments = self.comments or any(v.comment for v in self)
                inline = not has_comments and len(self) <= self.__inline_count__

                simp = []
                for link in self._links:
                    if link.key is None:
                        # this is a hidden link
                        simp.extend(link.value.__flatten__())
                    else:
                        # this is a normal key-value link

                        # fetch value
                        value = link.value._value_map[link]

                        # flatten value
                        tmp = value.__flatten__()
                        if tmp:
                            tmp[-1] += ","
                            if has_comments:
                                tmp[-1] = value.comment.apply(tmp[-1])
                        simp.extend(tmp)

                if inline:
                    if simp:
                        # remove trailing comma when inline
                        simp[-1] = simp[-1][:-1]
                    return ["[" + " ".join(simp) + "]"]
                return ["[", *((self.__indent__ + s) for s in simp), "]"]

            def __repr__(self):
                return "[" + ", ".join(repr(v) for v in self) + "]"

            def __pyobj__(self):  # type: () -> list
                return [value.__pyobj__() for value in self]

            def __hiddenobj__(self):
                is_root = self.root is self
                tmp = []
                for link in self._links:
                    if link.key is None:
                        value = link.value
                    else:
                        if is_root and link.scope is not self:
                            continue
                        value = link.value._value_map[link]
                        if isinstance(value, _Container):
                            value = value.__hiddenobj__()
                    tmp.append(value)
                return (Array, tmp)

            def _getstate(self, protocol=3):
                return (self.__hiddenobj__()[1],)

        return Array
