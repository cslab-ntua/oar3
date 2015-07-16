# -*- coding: utf-8 -*-
from __future__ import with_statement, absolute_import

import sys
import re
import threading
import contextlib

from collections import OrderedDict

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import (declarative_base, DeferredReflection,
                                        DeclarativeMeta)
from sqlalchemy.orm import scoped_session, sessionmaker, class_mapper
from sqlalchemy.orm.state import InstanceState
from sqlalchemy.orm.exc import UnmappedClassError

from alembic.migration import MigrationContext
from alembic.operations import Operations

from .utils import cached_property, merge_dicts
from .compat import iteritems, itervalues, reraise


__all__ = ['Database']


class BaseModel(object):

    __default_table_args__ = {
        'extend_existing': True,
        'sqlite_autoincrement': True
    }
    query = None

    @classmethod
    def create(cls, **kwargs):
        record = cls()
        for key, value in iteritems(kwargs):
            setattr(record, key, value)
        try:
            cls._db.session.add(record)
            cls._db.session.commit()
            return record
        except:
            exc_type, exc_value, tb = sys.exc_info()
            cls._db.session.rollback()
            reraise(exc_type, exc_value, tb.tb_next)

    def asdict(self, ignore_keys=()):
        data = OrderedDict()
        for key in get_entity_loaded_propnames(self):
            if key not in ignore_keys:
                data[key] = getattr(self, key)
        return data

    def __iter__(self):
        """Returns an iterable that supports .next()"""
        for (k, v) in iteritems(self.asdict()):
            yield (k, v)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class SessionProperty(object):

    def __init__(self):
        self._sessions = {}

    def _create_scoped_session(self, db):
        options = db._session_options
        options.setdefault('autoflush', True)
        options.setdefault('autocommit', False)
        options.setdefault('bind', db.engine)
        if db.query_class is None:
            from .basequery import BaseQuery
            db.query_class = BaseQuery
        options.setdefault('query_cls', db.query_class)
        return scoped_session(sessionmaker(**options))

    def __get__(self, obj, type):
        if obj is not None:
            if obj not in self._sessions:
                self._sessions[obj] = self._create_scoped_session(obj)
                obj.reflect()
            return self._sessions[obj]
        return self


class QueryProperty(object):

    def __init__(self, db):
        self._db = db

    def __get__(self, obj, type):
        session = self._db.session()
        try:
            mapper = class_mapper(type)
            if mapper:
                return self._db.query_class(mapper, session=session)
        except UnmappedClassError:
            return None


class Database(object):
    """This class is used to instantiate a SQLAlchemy connection to
    a database.
    """

    session = SessionProperty()
    query_class = None
    query_collection_class = None

    def __init__(self, uri=None, session_options=None):
        self.connector = None
        self._reflected = False
        self._cache = {"uri": uri}
        self._session_options = dict(session_options or {})
        self._engine_lock = threading.Lock()
        # Include some sqlalchemy orm functions
        _include_sqlalchemy(self)
        self.Model = declarative_base(cls=BaseModel, name='Model',
                                      metaclass=_BoundDeclarativeMeta)
        self.Model.query = QueryProperty(self)
        self.Model._db = self
        self.models = {}
        self.tables = {}

        class DeferredReflectionModel(DeferredReflection, self.Model):
            __abstract__ = True

        self.DeferredReflectionModel = DeferredReflectionModel

    @cached_property
    def uri(self):
        from oar.lib import config
        return config.get_sqlalchemy_uri()

    @property
    def op(self):
        ctx = MigrationContext.configure(self.engine)
        return Operations(ctx)

    @cached_property
    def queries(self):
        if self.query_collection_class is None:
            from .basequery import BaseQueryCollection
            self.query_collection_class = BaseQueryCollection
        return self.query_collection_class()

    @property
    def engine(self):
        """Gives access to the engine. """
        with self._engine_lock:
            if self.connector is None:
                self.connector = EngineConnector(self)
            return self.connector.get_engine()

    @cached_property
    def dialect(self):
        return self.engine.dialect.name

    @property
    def metadata(self):
        """Proxy for Model.metadata"""
        return self.Model.metadata

    @property
    def query(self):
        """Proxy for session.query"""
        return self.session.query

    def add(self, *args, **kwargs):
        """Proxy for session.add"""
        return self.session.add(*args, **kwargs)

    def flush(self, *args, **kwargs):
        """Proxy for session.flush"""
        return self.session.flush(*args, **kwargs)

    def commit(self):
        """Proxy for session.commit"""
        return self.session.commit()

    def rollback(self):
        """Proxy for session.rollback"""
        return self.session.rollback()

    def reflect(self, **kwargs):
        """Proxy for Model.prepare"""
        if not self._reflected:
            self.create_all()
            # autoload all tables marked for autoreflect
            self.DeferredReflectionModel.prepare(self.engine)
            self._reflected = True

    def create_all(self, bind=None, **kwargs):
        """Creates all tables. """
        if bind is None:
            bind = self.engine
        self.metadata.create_all(bind=bind, **kwargs)

    def delete_all(self, bind=None, **kwargs):
        """Drop all tables. """
        if bind is None:
            bind = self.engine
        with contextlib.closing(bind.connect()) as con:
            trans = con.begin()
            for table in itervalues(self.tables):
                con.execute(table.delete())
            trans.commit()

    def __contains__(self, member):
        return member in self.tables or member in self.models

    def __getitem__(self, name):
        if name in self:
            if name in self.tables:
                return self.tables[name]
            else:
                return self.models[name]
        else:
            raise KeyError(name)

    def close(self, **kwargs):
        """Proxy for Session.close"""
        with self._engine_lock:
            if self.connector is not None:
                self.session.close()
                self.connector.get_engine().dispose()
                self.connector = None

    def __repr__(self):
        engine = None
        if self.connector is not None:
            engine = self.engine
        return '<%s engine=%r>' % (self.__class__.__name__, engine)


class EngineConnector(object):

    def __init__(self, db):
        from oar.lib import config
        self._config = config
        self._db = db
        self._engine = None
        self._connected_for = None
        self._lock = threading.Lock()

    def apply_pool_defaults(self, options):
        def _setdefault(optionkey, configkey):
            value = self._config.get(configkey, None)
            if value is not None:
                options[optionkey] = value
        _setdefault('pool_size', 'SQLALCHEMY_POOL_SIZE')
        _setdefault('pool_timeout', 'SQLALCHEMY_POOL_TIMEOUT')
        _setdefault('pool_recycle', 'SQLALCHEMY_POOL_RECYCLE')
        _setdefault('max_overflow', 'SQLALCHEMY_MAX_OVERFLOW')
        _setdefault('convert_unicode', 'SQLALCHEMY_CONVERT_UNICODE')

    def apply_driver_hacks(self, info, options):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.
        """
        if info.drivername == 'mysql':
            info.query.setdefault('charset', 'utf8')
            options.setdefault('pool_size', 10)
            options.setdefault('pool_recycle', 3600)
            # TODO: More test
            # from MySQLdb.cursors import SSCursor as MySQLdb_SSCursor
            # if MySQLdb_SSCursor is not None:
            #     connect_args = options.get('connect_args', {})
            #     connect_args.update({'cursorclass': MySQLdb_SSCursor})
            #     options['connect_args'] = connect_args

        elif info.drivername == 'sqlite':
            no_pool = options.get('pool_size') == 0
            memory_based = info.database in (None, '', ':memory:')
            if memory_based and no_pool:
                raise ValueError(
                    'SQLite in-memory database with an empty queue'
                    ' (pool_size = 0) is not possible due to data loss.'
                )
        return options

    def get_engine(self):
        with self._lock:
            uri = self._db.uri
            echo = self._config['SQLALCHEMY_ECHO']
            if (uri, echo) == self._connected_for:
                return self._engine
            info = make_url(uri)
            options = {}
            self.apply_pool_defaults(options)
            self.apply_driver_hacks(info, options)
            if echo:
                options['echo'] = True
            self._engine = engine = create_engine(info, **options)
            self._connected_for = (uri, echo)
            return engine


def _include_sqlalchemy(db):
    import sqlalchemy

    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(db, key):
                setattr(db, key, getattr(module, key))
    db.event = sqlalchemy.event
    # Note: db.Table does not attempt to be a SQLAlchemy Table class.

    def _make_table(db):
        def _make_table(*args, **kwargs):
            if len(args) > 1 and isinstance(args[1], db.Column):
                args = (args[0], db.metadata) + args[1:]
            kwargs.setdefault('extend_existing', True)
            info = kwargs.pop('info', None) or {}
            info.setdefault('autoreflect', False)
            kwargs['info'] = info
            table = sqlalchemy.Table(*args, **kwargs)
            db.tables[table.name] = table
            return table
        return _make_table

    db.Table = _make_table(db)

    class Column(sqlalchemy.Column):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("nullable", False)
            super(Column, self).__init__(*args, **kwargs)

    db.Column = Column


class _BoundDeclarativeMeta(DeclarativeMeta):

    def __new__(cls, name, bases, d):
        if '__tablename__' not in d and '__table__' not in d and '__abstract__' not in d:
            d['__tablename__'] = get_table_name(name)
        default_table_args = d.pop('__default_table_args__',
                                   BaseModel.__default_table_args__)
        table_args = d.pop('__table_args__', {})
        if isinstance(table_args, dict):
            table_args = merge_dicts(default_table_args, table_args)
        elif isinstance(table_args, tuple):
            table_args = list(table_args)
            if isinstance(table_args[-1], dict):
                table_args[-1] = merge_dicts(default_table_args,
                                             table_args[-1])
            else:
                table_args.append(default_table_args)
            table_args = tuple(table_args)
        d['__table_args__'] = table_args
        return DeclarativeMeta.__new__(cls, name, bases, d)

    def __init__(self, name, bases, d):
        DeclarativeMeta.__init__(self, name, bases, d)
        if hasattr(bases[0], '_db'):
            bases[0]._db.models[name] = self
            bases[0]._db.tables[self.__table__.name] = self.__table__
            self._db = bases[0]._db


def get_table_name(name):
    def _join(match):
        word = match.group()
        if len(word) > 1:
            return ('_%s_%s' % (word[:-1], word[-1])).lower()
        return '_' + word.lower()
    return re.compile(r'([A-Z]+)(?=[a-z0-9])').sub(_join, name).lstrip('_')


def get_entity_loaded_propnames(entity):
    """Get entity property names that are loaded (e.g. won't produce new
    queries)

    :param entity: SQLAlchemy entity
    :returns: List of entity property names
    """
    ins = entity if isinstance(entity, InstanceState) else inspect(entity)
    columns = ins.mapper.column_attrs.keys() + ins.mapper.relationships.keys()
    keynames = set(columns)
    # If the entity is not transient -- exclude unloaded keys
    # Transient entities won't load these anyway, so it's safe to include
    # all columns and get defaults
    if not ins.transient:
        keynames -= ins.unloaded

    # If the entity is expired -- reload expired attributes as well
    # Expired attributes are usually unloaded as well!
    if ins.expired:
        keynames |= ins.expired_attributes
    return sorted(keynames, key=lambda x: columns.index(x))