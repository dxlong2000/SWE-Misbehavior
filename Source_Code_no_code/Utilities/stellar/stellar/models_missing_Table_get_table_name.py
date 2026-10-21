import hashlib
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_unique_hash():
    return hashlib.md5(str(uuid.uuid4()).encode('utf-8')).hexdigest()


class Snapshot(Base):
    __tablename__ = 'snapshot'
    id = sa.Column(
        sa.Integer,
        sa.Sequence('snapshot_id_seq'),
        primary_key=True
    )
    snapshot_name = sa.Column(sa.String(255), nullable=False)
    project_name = sa.Column(sa.String(255), nullable=False)
    hash = sa.Column(sa.String(32), nullable=False, default=get_unique_hash)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    worker_pid = sa.Column(sa.Integer, nullable=True)

    @property
    def slaves_ready(self):
        return self.worker_pid is None

    def __repr__(self):
        return "<Snapshot(snapshot_name=%r)>" % (
            self.snapshot_name
        )


class Table(Base):
    __tablename__ = 'table'
    id = sa.Column(sa.Integer, sa.Sequence('table_id_seq'), primary_key=True)
    table_name = sa.Column(sa.String(255), nullable=False)
    snapshot_id = sa.Column(
        sa.Integer, sa.ForeignKey(Snapshot.id), nullable=False
    )
    snapshot = sa.orm.relationship(Snapshot, backref='tables')

    def get_table_name(self, postfix, old=False):
        """This function generates a table name based on the given postfix and whether it is an old table. It first checks if there is a snapshot available and if the snapshot hash is not empty. If the snapshot is not available, it raises an Exception 'Table name requires snapshot'. If the snapshot hash is empty, it raises an Exception 'Snapshot hash is empty.' Then, it constructs the table name by concatenating the table name, snapshot hash, and postfix. If it is an old table, it returns a table name string formatted as 'stellar_{table name}{snapshot hash}{postfix}'. Otherwise, it returns a table name string generated using the hashlib module. It creates a hash by concatenating the table name, snapshot hash, and postfix with the pipe character ('|') in between. The resulting string is encoded in UTF-8 format and then hashed using MD5. The resulting hash is then converted to a hexadecimal string. The first 16 characters of the hexadecimal string are extracted and returned as the table name as 'stellar_{table name}'.
        Input-Output Arguments
        :param self: Table. An instance of the Table class.
        :param postfix: String. The postfix to be added to the table name.
        :param old: Bool. Whether it is an old table. Defaults to False.
        :return: String. The generated table name.
        """

    def __repr__(self):
        return "<Table(table_name=%r)>" % (
            self.table_name,
        )