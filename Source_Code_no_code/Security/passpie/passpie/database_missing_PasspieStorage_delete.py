from datetime import datetime
import logging
import os
import shutil

from tinydb import TinyDB, Storage, where, Query
import yaml


from .history import Repository
from .credential import split_fullname, make_fullname


class PasspieStorage(Storage):
    extension = ".pass"

    def __init__(self, path):
        super(PasspieStorage, self).__init__()
        self.path = path

    def make_credpath(self, name, login):
        dirname, filename = name, login + self.extension
        credpath = os.path.join(self.path, dirname, filename)
        return credpath

    def delete(self, credentials):
        """Delete the credentials from the PasspieStorage instance. It iterates over the list of credentials and deletes the corresponding files from the storage. If the directory containing the file becomes empty after deletion, it is also removed.
        Input-Output Arguments
        :param self: PasspieStorage. An instance of the PasspieStorage class.
        :param credentials: List of dictionaries. A list of credentials, where each credential is represented as a dictionary with "name" and "login" keys.
        :return: No return values.
        """

    def read(self):
        elements = []
        for rootdir, dirs, files in os.walk(self.path):
            filenames = [f for f in files if f.endswith(self.extension)]
            for filename in filenames:
                docpath = os.path.join(rootdir, filename)
                with open(docpath) as f:
                    elements.append(yaml.load(f.read()))

        return {"_default":
                {idx: elem for idx, elem in enumerate(elements, start=1)}}

    def write(self, data):
        from .utils import mkdir_open
        deleted = [c for c in self.read()["_default"].values()
                   if c not in data["_default"].values()]
        self.delete(deleted)

        for eid, cred in data["_default"].items():
            credpath = self.make_credpath(cred["name"], cred["login"])
            with mkdir_open(credpath, "w") as f:
                f.write(yaml.safe_dump(dict(cred), default_flow_style=False))


class Database(TinyDB):

    def __init__(self, config, storage=PasspieStorage):
        self.config = config
        self.path = config['path']
        self.repo = Repository(self.path,
                               autopull=config.get('autopull'),
                               autopush=config.get('autopush'))
        PasspieStorage.extension = config['extension']
        super(Database, self).__init__(self.path, storage=storage)

    def has_keys(self):
        return os.path.exists(os.path.join(self.path, '.keys'))

    def filename(self, fullname):
        login, name = split_fullname(fullname)
        return self._storage.make_credpath(name=name, login=login)

    def credential(self, fullname):
        login, name = split_fullname(fullname)
        Credential = Query()
        if login is None:
            creds = self.get(Credential.name == name)
        else:
            creds = self.get((Credential.login == login) & (Credential.name == name))
        return creds

    def add(self, fullname, password, comment):
        login, name = split_fullname(fullname)
        if login is None:
            logging.error('Cannot add credential with empty login. use "@<name>" syntax')
            return None
        credential = dict(fullname=fullname,
                          name=name,
                          login=login,
                          password=password,
                          comment=comment,
                          modified=datetime.now())
        self.insert(credential)
        return credential

    def update(self, fullname, values):
        login, name = split_fullname(fullname)
        values['fullname'] = make_fullname(values["login"], values["name"])
        values['modified'] = datetime.now()
        Credential = Query()
        if login is None:
            query = (Credential.name == name)
        else:
            query = ((Credential.login == login) & (Credential.name == name))
        self.table().update(values, query)

    def credentials(self, fullname=None):
        if fullname:
            login, name = split_fullname(fullname)
            Credential = Query()
            if login is None:
                creds = self.search(Credential.name == name)
            else:
                creds = self.search((Credential.login == login) & (Credential.name == name))
        else:
            creds = self.all()
        return sorted(creds, key=lambda x: x["name"] + x["login"])

    def remove(self, fullname):
        self.table().remove(where('fullname') == fullname)

    def matches(self, regex):
        Credential = Query()
        credentials = self.search(
            Credential.name.matches(regex) |
            Credential.login.matches(regex) |
            Credential.comment.matches(regex)
        )
        return sorted(credentials, key=lambda x: x["name"] + x["login"])