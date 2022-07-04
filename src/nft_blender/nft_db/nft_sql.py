#!$BLENDER_PATH/python/bin python

import pathlib

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.orm.exc
import sqlalchemy.ext.declarative


class DB_ObjectBase(object):
    """"""
    def __getitem__(self, field):
        return self.__dict__[field]

    def __repr__(self):
        """"""
        return f'<{self.__class__.__name__} (id: {self.id} in {self.__tablename__})>'

    @sqlalchemy.ext.declarative.declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id =  sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)


DB_ObjectBase = sqlalchemy.ext.declarative.declarative_base(cls=DB_ObjectBase)


DB_UserProjects = sqlalchemy.Table(
    'user_projects',
    DB_ObjectBase.metadata,
    sqlalchemy.Column('project_id', sqlalchemy.ForeignKey('projects.id'), primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.ForeignKey('users.id'), primary_key=True),
)


class DB_Project(DB_ObjectBase):
    """"""
    __tablename__ = 'projects'
    code = sqlalchemy.Column(sqlalchemy.String, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    path = sqlalchemy.Column(sqlalchemy.String)
    pipeline = sqlalchemy.Column(sqlalchemy.JSON)
    users = sqlalchemy.orm.relationship(
        'DB_User',
        order_by='DB_User.id',
        secondary=DB_UserProjects,
        back_populates='projects',
    )


class DB_User(DB_ObjectBase):
    """"""
    __tablename__ = 'users'
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    projects = sqlalchemy.orm.relationship(
        'DB_Project',
        order_by='DB_Project.id',
        secondary=DB_UserProjects,
        back_populates='users',
    )


def db_create_table(
    db_engine: sqlalchemy.engine.base.Engine,
    drop_existing: bool = False
):
    """"""
    if drop_existing:
        DB_ObjectBase.metadata.drop_all(db_engine)

    DB_ObjectBase.metadata.create_all(db_engine)


def db_get_columns(db_row: DB_ObjectBase) -> dict:
    """"""
    return db_row.__class__.__table__.columns


def db_get_engine(db_url: pathlib.Path | str):
    """"""
    return sqlalchemy.create_engine(db_url, echo=True)


def db_get_url(
    db_name: str,
    root_dir_path: pathlib.Path | str,
) -> pathlib.Path:
    """SQLite only"""
    root_dir_path = pathlib.Path(root_dir_path)
    db_file_path = root_dir_path.joinpath(db_name).with_suffix('.db')
    db_url = f'sqlite:///{db_file_path.as_posix()}'

    return db_url


def db_upsert(
    db_engine: sqlalchemy.engine.base.Engine,
    column_name_filter: str,
    *db_entries: tuple[DB_ObjectBase],
) -> bool | tuple[bool]:
    """"""
    db_entries_updated = []

    with sqlalchemy.orm.Session(db_engine) as db_session:

        for db_entry in db_entries:

            try:

                db_col_attr = db_entry.__class__.__table__.columns[column_name_filter]

                db_query = db_session.query(db_entry.__class__) \
                                     .filter(db_col_attr == db_entry[column_name_filter])

                if db_query.one_or_none() is None:

                    db_session.add(db_entry)

                else:

                    for k, v in db_get_columns(db_entry).items():
                        if not v.primary_key:
                            db_query.update({k: db_entry[k]})


            except sqlalchemy.orm.exc.MultipleResultsFound as sqle:

                print(f'Database error: {sqle}.')
                print('Two or more tables found with the same name: {db_entry.name}.')
                db_entries_updated.append(False)

            except Exception as e:
                print(f'Database error: {e}.')
                db_entries_updated.append(False)

            finally:

                db_session.flush()
                db_entries_updated.append(True)

        db_session.commit()

    return tuple(db_entries_updated) if len(db_entries) > 1 else db_entries_updated[0]
