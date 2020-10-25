import sqlalchemy
from eaf_project.database import engine

metadata = sqlalchemy.MetaData()
elements = sqlalchemy.Table(
    "elements",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
)

commodity = sqlalchemy.Table(
    "commodity",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("inventory", sqlalchemy.Float),
    sqlalchemy.Column("price", sqlalchemy.Float),
    sqlalchemy.Column("chemical_composition", sqlalchemy.String)
)

user = sqlalchemy.Table(
    "user",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String)
)

metadata.create_all(engine)