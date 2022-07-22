#!$BLENDER_PATH/python/bin python

import logging
import pathlib
import sys
import typing

import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.orm.exc
import sqlalchemy.util._collections


__LOGGER__ = logging.getLogger(__name__)
__LOGGER__.addHandler(logging.StreamHandler(sys.stdout))
__LOGGER__.setLevel(logging.INFO)


class DBObjectBase(object):
    """TODO"""
    def __getitem__(self, field):
        """TODO"""
        return self.__dict__[field]

    def __repr__(self):
        """TODO"""
        return f'<{self.__class__.__name__} (id: {self.id} in {self.__tablename__})>'

    @sqlalchemy.ext.declarative.declared_attr
    def __tablename__(cls):
        """TODO"""
        return cls.__name__.lower()

    id =  sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)


DBObjectBase = sqlalchemy.ext.declarative.declarative_base(cls=DBObjectBase)


DBUserProjects = sqlalchemy.Table(
    'user_projects',
    DBObjectBase.metadata,
    sqlalchemy.Column('project_id', sqlalchemy.ForeignKey('projects.id'), primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id'), primary_key=True),
)


class DBProject(DBObjectBase):
    """TODO"""
    __tablename__ = 'projects'
    code = sqlalchemy.Column(sqlalchemy.String, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    pipeline = sqlalchemy.Column(sqlalchemy.JSON)
    users = sqlalchemy.orm.relationship(
        'DBUser',
        order_by='DBUser.id',
        secondary=DBUserProjects,
        back_populates='projects',
    )


class DBUser(DBObjectBase):
    """TODO"""
    __tablename__ = 'users'
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    projects = sqlalchemy.orm.relationship(
        'DBProject',
        order_by='DBProject.id',
        secondary=DBUserProjects,
        back_populates='users',
    )


DBModels = (DBProject, DBUser)


def db_create_table(
    db_engine: sqlalchemy.engine.base.Engine,
    drop_existing: bool = False,
):
    """TODO"""
    if drop_existing:
        DBObjectBase.metadata.drop_all(db_engine)

    DBObjectBase.metadata.create_all(db_engine)


def db_delete_rows(
    db_engine: sqlalchemy.engine.base.Engine,
    db_cls: DBObjectBase | sqlalchemy.Table,
    filters: typing.Iterable[tuple[str, object]] = (),
):
    """TODO"""
    db_table = sqlalchemy.Table if isinstance(db_cls, sqlalchemy.Table) else db_cls.__table__
    db_del = sqlalchemy.delete(db_table)
    for col_attr_name, col_val in filters:
        col_attr = db_table.columns[col_attr_name]
        db_del = db_del.where(col_attr == col_val)

    db_engine.execute(db_del)


def db_get_columns(db_row: DBObjectBase) -> dict:
    """TODO"""
    return db_row.__class__.__table__.columns


def db_get_engine(
    db_url: pathlib.Path | str,
) -> sqlalchemy.engine.base.Engine | None:
    """TODO"""
    try:
        return sqlalchemy.create_engine(db_url, echo=True)
    except sqlalchemy.exc.ArgumentError:
        return None


def db_get_metadata(
    db_engine: sqlalchemy.engine.base.Engine,
) -> sqlalchemy.util._collections.FacadeDict:
    """TODO"""
    db_metadata = sqlalchemy.MetaData(bind=db_engine)
    db_metadata.reflect()

    return db_metadata


def db_get_url(
    db_name: str,
    root_dir_path: pathlib.Path | str,
    dbms_name: str = 'SQLite',
) -> str:
    """SQLite only"""
    root_dir_path = pathlib.Path(root_dir_path)
    db_file_path = root_dir_path.joinpath(db_name).with_suffix('.db')
    db_url = ''

    if dbms_name == 'SQLite':
        db_url = f'sqlite:///{db_file_path.as_posix()}'

    return db_url


def db_query_basic(
    db_engine: sqlalchemy.engine.base.Engine,
    db_cls: DBObjectBase,
    limit: int = -1,
    columns: typing.Sequence = (),
    filters: typing.Iterable[tuple[str, object]] = (),
) -> list:
    """TODO"""
    results = []

    with sqlalchemy.orm.Session(db_engine) as db_session:
        db_query = db_session.query(db_cls)
        db_query.options(sqlalchemy.orm.load_only(columns))

        for col_attr_name, col_val in filters:
            col_attr = db_cls.__table__.columns[col_attr_name]
            db_query = db_query.filter(col_attr == col_val)

        if db_query.first() is not None:
            if limit < 0:
                results.extend(db_query.all())
            elif limit == 1:
                results.append(db_query.one())
            else:
                results.extend(db_query.limit(limit))

    return results


def db_test_connection(
    db_engine: sqlalchemy.engine.base.Engine = None
) -> bool:
    """TODO"""
    try:
        assert isinstance(db_engine, sqlalchemy.engine.base.Engine)
        db_engine.connect()
        __LOGGER__.info('Database connection verified.')

        return True

    except (AssertionError, sqlalchemy.exc.SQLAlchemyError) as sqle:
        logger_msg = f'Database error: {sqle}.'
        __LOGGER__.warning(logger_msg)

        return False


def db_upsert(
    db_engine: sqlalchemy.engine.base.Engine,
    db_entries: typing.Iterable[DBObjectBase] = (),
    column_name_filter: str = None,
) -> bool | tuple[bool]:
    """TODO"""
    db_entries_updated = []

    with sqlalchemy.orm.Session(db_engine) as db_session:

        for db_entry in db_entries:

            try:
                db_cls = db_entry.__class__
                # Query the DB using a simple equal operator for the given column attribute.
                if column_name_filter:
                    db_col_attr = db_cls.__table__.columns[column_name_filter]
                    db_query = db_session.query(db_cls) \
                                         .filter(db_col_attr == db_entry[column_name_filter])

                # Otherwise default to querying using the Primary Key column, aka "id".
                else:
                    db_query = db_session.query(db_cls).get(db_entry.id)

                # If no results are found, add the entry to the DB
                if db_query.one_or_none() is None:
                    db_session.add(db_entry)
                    logger_msg = f'{db_cls} entry added for {db_entry}.'
                    __LOGGER__.debug(logger_msg)

                # Otherwise, update all columns for the existing entry.
                else:
                    for key, val in db_get_columns(db_entry).items():
                        if not val.primary_key:
                            db_query.update({key: db_entry[key]})
                    logger_msg = f'{db_cls} entry updated for {db_entry}.'
                    __LOGGER__.debug(logger_msg)

            except sqlalchemy.orm.exc.MultipleResultsFound as sqle:
                logger_msg = f'Database error: {sqle}. \
                               Two or more tables found with the same name: {db_entry.name}.'
                __LOGGER__.warning(logger_msg)
                db_entries_updated.append(False)

            except sqlalchemy.exc.SQLAlchemyError as sqle:
                logger_msg = f'Database error: {sqle}.'
                __LOGGER__.warning(logger_msg)
                db_entries_updated.append(False)

            finally:
                db_session.flush()
                db_entries_updated.append(True)

        db_session.commit()

    return tuple(db_entries_updated)
