# -*- coding: utf-8 -*-
from collections.abc import MutableSequence, Sequence, Mapping
from queue import LifoQueue
from ..exceptions import MixedArrayTypesError
from ._utils import flatten
from ._items import _Container, Comment, _Value
from .key import Key, HiddenKey


class _Link(object):
    __slots__ = "key", "value", "__weakref__"

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self.key)


class _Links(list):
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
        try:
            while True:
                self.pop()
        except (KeyError, IndexError):
            pass

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


def check_state(container, f):
    # bubble up to the root finding all containers that would need to be moved if the
    # innermost container's complexity changes
    containers = []
    while container._parent != container:
        if isinstance(container, Array):
            prior = containers[0] if containers else None

            # Tables preceding the prior are prepended
            # the prior is skipped
            # Tables after the prior are prepended

            i = 0
            for c in container:
                if c is prior:
                    i = len(containers)
                else:
                    containers.insert(i, c)
                i += 1
        containers.insert(0, container)

        container = container._parent

    if containers:
        container = containers[0]

        def _(*args, **kwargs):
            # store initial inline state
            inline = container.inline

            # perform function
            tmp = f(*args, **kwargs)

            # determine whether the inline state changes
            if container.inline == inline:
                # no state change
                pass
            else:
                for c in containers:
                    if container.complex:
                        # move to root scope
                        assert c._scopes.qsize() == 1

                        # old scope (where the value is stored)
                        oscope = c._scopes.get()
                        # new scope (where the value is moving to)
                        nscope = c.root
                        c._scopes.put(nscope)
                    else:
                        # move to local scope
                        assert c._scopes.qsize() == 2

                        # old scope (where the value is stored)
                        oscope = c._scopes.get()
                        # new scope (where the value is moving to)
                        nscope = c._scopes.get()
                        # nscope was the last scope in queue and hence wasn't removed

                    # virtual scope (where the value appears to be stored)
                    vscope = c._parent

                    # get/remove link/value from old scope
                    link = oscope._links.pop(c._prefix)
                    value = oscope._values_map.pop(link.key)

                    # update scope
                    vscope._scope_map[link.key[-1]] = nscope
                    # insert value
                    nscope._values_map[link.key] = value
                    # insert link
                    nscope._links.append(link)

            # return function result(s)
            return tmp

        return _
    return f


class _ScopeQueue(LifoQueue):
    # custom LIFO queue
    #   - maxsize=2
    #   - first element inserted is never removed
    def __init__(self):
        super(_ScopeQueue, self).__init__(maxsize=2)

    def _get(self):
        # never remove the first element
        if len(self.queue) == 1:
            return self.queue[0]
        return self.queue.pop()


class Comments(list):
    def __init__(self, container):
        self._container = container

    def __check__(self, f):
        return check_state(self._container, f)

    def __getitem__(self, index):
        link = self._container._links[index]

        if link.key is not None:
            raise IndexError("Cannot get {}".format(index))

        return link.value

    def __setitem__(self, index, value):
        link = self._container._links[index]

        if link.key is not None:
            raise IndexError("Cannot set {}".format(index))

        link.value = Comment(value)

    def __delitem__(self, index):
        link = self._container._links[index]

        if link.key is not None:
            raise IndexError("Cannot delete {}".format(index))

        __delitem__ = self.__check__(self._container._links.__delitem__)
        __delitem__(index)

    def __len__(self):
        # number of comments is the number of links - number of keys
        return len(self._container._links) - len(self._container._links._map)

    def __bool__(self):
        return len(self) > 0

    def __iter__(self):
        for link in self._container._links:
            if link.key is None:
                yield link.value

    def __str__(self):
        raise NotImplementedError("Cannot convert to string")

    def __repr__(self):
        return "{{{}}}".format(
            ", ".join(
                "{}: {!r}".format(i, link.value)
                for i, link in enumerate(self._container._links)
                if link.key is None
            )
        )

    def insert(self, index, value):
        link = _Link()
        link.key = None
        link.value = Comment(value)

        insert = self.__check__(self._container._links.insert)
        insert(index, link)

    def append(self, value):
        self.insert(len(self._container._links), value)


class _Scalars(_Container):
    def scalars():
        def fget(self):
            return self._scalars

        def fset(self, scalars):
            scalars = list(scalars)
            if any(not isinstance(s, _Value) for s in scalars):
                raise TypeError("scalars must be a list of _Value")
            self._scalars = scalars

        return locals()

    scalars = property(**scalars())


class Table(_Scalars, dict):
    __inline_count__ = 3

    def __new__(cls, value=None, parent=None, prefix=()):
        if isinstance(value, cls):
            return value

        self = super(Table, cls).__new__(cls)

        if parent is None:
            parent = self
        else:
            assert isinstance(parent, _Container)
        self._parent = parent
        self._prefix = prefix

        self._scopes = _ScopeQueue()
        self._scope_map = {}
        self._values_map = {}
        self._links = _Links()
        self._comments = Comments(self)

        if value:
            self.update(value)

        return self

    def __init__(self, value=None, parent=None, prefix=()):
        super(Table, self).__init__()

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
    def comments(self):  # type: () -> Comments
        return self._comments

    @property
    def inline(self):
        try:
            return not self._complex
        except AttributeError:
            pass

        # if self is the root then we remember that as perpetually complex
        if self.root is self:
            self._complex = True
            return not self._complex

        # a table is considered inline if:
        #        there are no comments
        #   and  it has less than __inline_count__ values
        #   and  none of the values are complex
        return bool(
            not self._comments
            and len(self) <= self.__inline_count__
            and not any(v.complex for v in self.values())
        )

    def complex():
        def fget(self):
            return not self.inline

        def fset(self, value):
            if value is None:
                return

            value = bool(value)
            if value is not True:
                raise ValueError(
                    "Cannot set complexity to False, complexity state can only be set "
                    "to True OR deleted."
                )
            self.__check__(lambda: setattr(self, "_complex", value))()

        def fdel(self):
            self.__check__(lambda: delattr(self, "_complex"))()

        return locals()

    complex = property(**complex())

    def __check__(self, f):
        return check_state(self, f)

    def __getitem__(self, key):
        rkey = ()
        if isinstance(key, tuple):
            key, *rkey = key
        rkey = tuple(rkey)

        link = super(Table, self).__getitem__(key)
        scope = self._scope_map[link.key[-1]]
        value = scope._values_map[link.key]

        if rkey:
            return value.__getitem__(rkey)
        return value

    def setdefault(self, key, value):
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return self[key]

    def __setitem__(self, key, value, scope=None):
        if isinstance(key, tuple):
            if len(key) > 1:
                key, *rkey = key
                rkey = tuple(rkey)
                container = self.setdefault(key, {})
                scope = self if scope is None else scope
                return container.__setitem__(rkey, value, scope)
            key = key[0]

        try:
            link = super(Table, self).__getitem__(key)

            set_value = self.__check__(self._set_value)
            set_value(link, value, scope)
        except KeyError:
            link = _Link()
            link.key = (*self._prefix, Key(key))
            link.value = None

            add_link = self.__check__(self._add_link)
            add_link(link, value, scope)

            super(Table, self).__setitem__(link.key[-1], link)

    def insert(self, index, key, value):
        try:
            if key in self:
                raise IndexError("Cannot reinsert a key that is already set")
        except KeyError:
            link = _Link()
            link.key = (*self._prefix, Key(key))
            link.value = None

            add_link = self.__check__(self._add_link)
            add_link(link, value)

            super(Table, self).__setitem__(link.key[-1], link)

    def _check_scope(self, value, scope):
        if scope != self.root and value.complex:
            scope = self.root
            value._scopes.put(scope)

        return scope

    def _set_value(self, link, value, scope=None):
        # this is every containers "original" inline scope
        scope = self if scope is None else scope

        if isinstance(value, Mapping):
            value = Table(value=value, parent=self, prefix=link.key)
            value._scopes.put(scope)
            scope = self._check_scope(value, scope)
        elif isinstance(value, Sequence) and not isinstance(value, (str, tuple)):
            value = Array(value=value, parent=self, prefix=link.key)
            value._scopes.put(scope)
            scope = self._check_scope(value, scope)
        else:
            args = value if isinstance(value, tuple) else (value,)
            for scalar in self.scalars:
                try:
                    value = scalar(*args)
                    break
                except TypeError:
                    pass

            if not isinstance(value, _Value):
                raise TypeError(
                    "Cannot convert {} to valid types ({})".format(
                        value, ", ".join(scalar.__name__ for scalar in self.scalar)
                    )
                )

        scope = self._scope_map.setdefault(link.key[-1], scope)

        scope._values_map[link.key] = value

        return scope

    def _add_link(self, link, value, scope=None):
        scope = self._set_value(link, value, scope)

        # store a link into the scope such that we can properly render the toml
        scope._links.append(link)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError(
                "update expected at most 1 arguments, got {}".format(len(args))
            )

        if args:
            arg = args[0]
            if isinstance(arg, Table):
                for link in arg._links:
                    if link.key is None:
                        self._comments.append(link.value)
                    else:
                        self[link.key] = arg[link.key[-1]]
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

    def __delitem__(self, key):
        if isinstance(key, tuple):
            del self.__getitem__(key[:-1])[key[-1]]
            return

        fullkey = (*self._prefix, key)
        scope = self._scope_map.pop(key)

        # remove the link
        del scope._links[fullkey]

        value = super(Table, self).__getitem__(key)
        super(Table, self).__delitem__(key)

        if isinstance(value, Mapping):
            # this is a nested container
            for key in list(value.keys()):
                del value[key]
        del scope._values_map[fullkey]

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

    def __flatten__(self):
        simp = []
        comp = []

        first = len(self._prefix)

        # if this the root and it has a comment then we want to insert its
        # comment at the top
        if self.root == self and self.comment:
            simp.append(flatten(self.comment))

        for link in self._links:
            if link.key is None:
                simp.append(flatten(link.value))
            else:
                value = self._values_map[link.key]
                key = []
                for k in link.key[first:]:
                    key.extend(k.__flatten__())
                key = ".".join(key)

                if isinstance(value, Table) and (
                    value.complex
                    or (isinstance(value._parent, Array) and value._parent.complex)
                ):
                    key = "[{}]".format(key)

                    # if this table is inside of an Array it's an AoT
                    if isinstance(value._parent, Array):
                        key = "[{}]".format(key)

                    # comments are applied directly to the key
                    key = value.comment.apply(key)

                    # if we already have tables from before, put a newline between
                    # them and this
                    if comp:
                        comp.append("")

                    # insert the key and the
                    comp.append(key)
                    comp.extend(value.__flatten__())
                elif isinstance(value, Array) and value.complex:
                    # the complex array itself is not displayed, the individual Tables
                    # have already been linked into root so they will be displayed there
                    pass
                else:
                    tvalue = value.comment.apply(flatten(value))
                    simp.append("{} = {}".format(key, tvalue))

        if self.inline and (not isinstance(self._parent, Array) or self._parent.inline):
            # this is an inline table, join with commas and style with {}
            return ["{{{}}}".format(", ".join(simp))]
        if simp and comp:
            # we have both, put a newline between them
            return simp + [""] + comp
        # return the one that has stuff
        return simp or comp

    def __repr__(self):
        return "{{{}}}".format(
            ", ".join("{!r}: {!r}".format(k, v) for k, v in self.items())
        )

    def __pyobj__(self):  # type: () -> dict
        return {key.__pyobj__(): value.__pyobj__() for key, value in self.items()}


class Array(_Scalars, list):
    __inline_count__ = 3
    __indent__ = 4

    def __new__(cls, value=None, parent=None, prefix=()):
        if isinstance(value, cls):
            return value

        self = super(Array, cls).__new__(cls)

        assert isinstance(parent, _Container)
        self._parent = parent
        self._prefix = prefix

        self._scopes = _ScopeQueue()
        self._scope_map = {}
        self._values_map = {}
        self._links = _Links()
        self._comments = Comments(self)

        if value:
            self.extend(value)

        return self

    def __init__(self, value=None, parent=None, prefix=()):
        super(Array, self).__init__()

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
                return Table
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
    def inline(self):
        return not self.complex

    def complex():
        def fget(self):
            try:
                return self._complex
            except AttributeError:
                pass

            # if type is Table then we remember that as perpetually complex
            if self.type == Table:
                self._complex = True
                return not self._complex

            # an array is considered complex if:
            #        its type is Table
            #   and  any of the tables are complex
            return bool(any(t.complex for t in self))

        def fset(self, value):
            if value is None:
                return

            value = bool(value)
            if value is not True:
                raise ValueError(
                    "Cannot set complexity to False, complexity state can only be set "
                    "to True OR deleted."
                )
            if self.type not in (Table, None):
                raise ValueError("Cannot change complexity of a inline array.")
            self.__check__(lambda: setattr(self, "_complex", value))()

        def fdel(self):
            self.__check__(lambda: delattr(self, "_complex"))()

        return locals()

    complex = property(**complex())

    def __check__(self, f):
        return check_state(self, f)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return [self[i] for i in range(index.start, index.stop, index.step)]

        rindex = ()
        if isinstance(index, tuple):
            index, *rindex = index
        rindex = tuple(rindex)

        link = super(Array, self).__getitem__(index)

        try:
            scope = self._scope_map[link.key[-1]]
            value = scope._values_map[link.key]
        except KeyError:
            raise IndexError("list index out of range")

        if rindex:
            return value.__getitem__(rindex)
        return value

    # allow scope to be passed in, juse done use it
    def __setitem__(self, index, value, scope=None):
        if isinstance(index, tuple):
            if len(index) > 1:
                index, *rindex = index
                rindex = tuple(rindex)

                container = self[index]

                return container.__setitem__(rindex, value)
            index = index[0]

        link = super(Array, self).__getitem__(index)

        set_value = self.__check__(self._set_value)
        set_value(link, value)

    def insert(self, index, value):
        link = _Link()
        link.key = (*self._prefix, HiddenKey())
        link.value = None

        add_link = self.__check__(self._add_link)
        add_link(link, value)

        super(Array, self).insert(index, link)

    def _check_scope(self, value, scope):
        if scope != self.root and value.complex:
            scope = self.root
            value._scopes.put(scope)

        return scope

    def _set_value(self, link, value, scope=None):
        # this is every containers "original" inline scope
        scope = self if scope is None else scope

        if isinstance(value, Mapping) and (not self.type or self.type == Table):
            value = Table(value=value, parent=self, prefix=link.key)
            value._scopes.put(scope)
            scope = self._check_scope(value, scope)
        elif (
            isinstance(value, Sequence)
            and not isinstance(value, (str, tuple))
            and (not self.type or self.type == Array)
        ):
            value = Array(value=value, parent=self, prefix=link.key)
            value._scopes.put(scope)
            scope = self._check_scope(value, scope)
        else:
            args = value if isinstance(value, tuple) else (value,)
            for scalar in self.scalars:
                try:
                    value = scalar(*args)
                    break
                except TypeError:
                    pass

            if self.type and not isinstance(value, self.type):
                raise MixedArrayTypesError

        scope = self._scope_map.setdefault(link.key[-1], scope)

        scope._values_map[link.key] = value

        return scope

    def _add_link(self, link, value, scope=None):
        scope = self._set_value(link, value, scope)

        # store a link into the scope such that we can properly render the toml
        scope._links.append(link)

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
                    if isinstance(value, Comments):
                        self._comments.append(value)
                    else:
                        self.append(value)

    def append(self, value):
        self.insert(len(self), value)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __flatten__(self):  # type: () -> str
        txt = []

        # we use newlines if there are any comments
        newline = self._comments or any(v.comment for v in self)

        for link in self._links:
            if link.key is None:
                txt.append(flatten(link.value))
            else:
                value = self._values_map[link.key]
                tvalue = value.__flatten__()
                if newline:
                    tvalue[-1] = value.comment.apply(tvalue[-1] + ",")
                else:
                    tvalue[-1] += ","
                txt.extend(tvalue)

        if not newline:
            if len(txt) <= self.__inline_count__:
                if txt:
                    txt[-1] = txt[-1][:-1]
                return ["[{}]".format(" ".join(txt))]
            return ["[", *((" " * self.__indent__) + t for t in txt), "]"]
        return ["[", *((" " * self.__indent__) + t for t in txt), "]"]

    def __repr__(self):
        return "[{}]".format(", ".join(repr(v) for v in self))

    def __pyobj__(self):  # type: () -> datetime
        return [value.__pyobj__() for value in self]
