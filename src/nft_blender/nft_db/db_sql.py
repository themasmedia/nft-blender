#!$BLENDER_PATH/python/bin python

"""
NFT Blender - DB - SQL

"""

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
    """
    The base class for SQLAlchemy database entries/rows.
    """
    #: Primary key identifier property (Integer)
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    def __getitem__(self, field: str) -> object:
        """
        Returns the value for a given field using a dictionary key interface.

        :param field: Name of the property field (i.e. "id")
        """
        return self.__dict__[field]

    def __repr__(self) -> str:
        """
        Returns a human-readable representation of the object.
        """
        return f'<{self.__class__.__name__} (id: {self.id} in {self.__tablename__})>'

    @classmethod
    @sqlalchemy.ext.declarative.declared_attr
    def __tablename__(cls) -> str:
        """
        Returns the table name of the entry as a SQLAlchemy declared attribute.
        """
        return cls.__name__.lower()


# Declare the DBObjectBase class as the base class for all DB entries.
DBObjectBase = sqlalchemy.ext.declarative.declarative_base(
    cls=DBObjectBase, name=DBObjectBase.__name__
)

# Association table between projects and users.
# TODO Not yet functional.
DBUserProjects = sqlalchemy.Table(
    'user_projects',
    DBObjectBase.metadata,
    sqlalchemy.Column('project_id', sqlalchemy.ForeignKey('projects.id'), primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id'), primary_key=True),
)


class DBProject(DBObjectBase):
    """
    The database entry class for projects.
    """
    __tablename__ = 'projects'
    #: Unique project code property (String)
    code = sqlalchemy.Column(sqlalchemy.String, unique=True)
    #: Unique project name property (String)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    #: Project disk location path property (String)
    path = sqlalchemy.Column(sqlalchemy.String)
    #: Project disk location path property (JSON)
    pipeline = sqlalchemy.Column(sqlalchemy.JSON)
    #: Users relationship property (DBUser)
    # users = sqlalchemy.orm.relationship(
    #     'DBUser',
    #     order_by='DBUser.id',
    #     secondary=DBUserProjects,
    #     back_populates='projects',
    # )


class DBUser(DBObjectBase):
    """
    The database entry class for users.
    """
    __tablename__ = 'users'
    #: Unique user name property (String)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    #: Users relationship property (DBProject)
    # projects = sqlalchemy.orm.relationship(
    #     'DBProject',
    #     order_by='DBProject.id',
    #     secondary=DBUserProjects,
    #     back_populates='users',
    # )


DBModels = (DBProject, DBUser)


def db_create_table(
    db_engine: sqlalchemy.engine.base.Engine,
    drop_existing: bool = False,
) -> None:
    """
    Check for existence of Tables with Engine metadata, and create them if necessary.
    https://docs.sqlalchemy.org/en/14/core/metadata.html#creating-and-dropping-database-tables

    :param db_engine: The connected Engine.
    :param drop_existing: If True,
        drop the table(s) in the engine metadata to reset schema
        before creating Tables (default: False).
    """
    if drop_existing:
        DBObjectBase.metadata.drop_all(db_engine)

    DBObjectBase.metadata.create_all(db_engine)


def db_delete_rows(
    db_engine: sqlalchemy.engine.base.Engine,
    db_cls: typing.Union[DBObjectBase,sqlalchemy.Table],
    filters: typing.Iterable[typing.Sequence] = (),
) -> None:
    """
    Deletes the specified Row(s) that match the query filter(s).

    :param db_engine: The connected Engine.
    :param db_cls: The entry (or entry's Table) class of the Rows to delete.
    :param filters: The attribute name(s) and value(s) used to query for Rows to delete.
        Each filter is submitted as a tuple: (str, object)
    """
    db_table = sqlalchemy.Table if isinstance(db_cls, sqlalchemy.Table) else db_cls.__table__
    db_del = sqlalchemy.delete(db_table)
    for col_attr_name, col_val in filters:
        col_attr = db_table.columns[col_attr_name]
        db_del = db_del.where(col_attr == col_val)

    db_engine.execute(db_del)


def db_get_columns(db_row: DBObjectBase) -> dict:
    """
    Gets all Columns for a given row in a Table.

    :param db_row: The row object to query columns on.
    :returns: The column names and values for the row.
    """
    return db_row.__class__.__table__.columns


def db_get_engine(
    db_url: typing.Union[pathlib.Path, str],
) -> typing.Union[sqlalchemy.engine.base.Engine, None]:
    """
    Creates a SQLAlchemy Engine for the given DB url (connects automatically, if able).

    :param db_url: The DBMS-formatted database url.
    :returns: The Engine for the database.
    """
    try:
        return sqlalchemy.create_engine(db_url, echo=True)
    except sqlalchemy.exc.ArgumentError:
        return None


def db_get_metadata(
    db_engine: sqlalchemy.engine.base.Engine,
) -> sqlalchemy.util._collections.FacadeDict:
    """
    Get the table metadata for all available Table entries in a database.

    :param db_engine: The connected Engine.
    :returns: Metadata for the Engine.
    """
    db_metadata = sqlalchemy.MetaData(bind=db_engine)
    db_metadata.reflect()

    return db_metadata


def db_get_url(
    db_name: str,
    db_root_path: str,
    dbms_name: str = 'SQLite',
) -> str:
    """
    Generates the DBMS-formatted database url for the given path.
    Only SQLite is supported at this time (uses user's local disk as database location).

    :param db_root_path: Path string to format.
    :returns: the DBMS-formatted database url.
    """
    if dbms_name == 'SQLite':
        db_root_path = pathlib.Path(db_root_path)
        db_file_path = db_root_path.joinpath(db_name).with_suffix('.db')

        return f'sqlite:///{db_file_path.as_posix()}'

    return ''


def db_query_basic(
    db_engine: sqlalchemy.engine.base.Engine,
    db_cls: DBObjectBase,
    limit: int = -1,
    columns: typing.Sequence[sqlalchemy.Column] = (),
    filters: typing.Iterable[typing.Sequence] = (),
) -> list:
    """
    Queries Table(s) for Rows that match the given arguments.

    :param db_engine: The connected Engine.
    :param db_cls: Entry class for Rows to query.
    :param limit: Total number of results to return.
    :param columns: Load only the specified Column(s) for matching Row(s).
    :param filters: The attribute name(s) and value(s) used to query for Rows to delete.
    :returns: List of matching Rows.
    """
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
    """
    Tests if the Engine is connected.

    :param db_engine: The connected Engine.
    :returns: Status of the connection.
    """
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
) -> tuple[bool]:
    """
    Upserts the given entries as Rows (Rows are updated if they exist or created if they don't).
    If a filter is given, existing Rows that match values in the entr(ies) will be updated.

    :param db_engine: The connected Engine.
    :returns: Success results for each upsert operation for each Row (ordered by entries given).
    """
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
