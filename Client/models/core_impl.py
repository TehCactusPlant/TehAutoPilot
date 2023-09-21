import logging
from Client.database.models import DBModel
import Client.database.core as core_db

ROOT_DB = "C:\\Users\\Cactus\\Documents\\pkmnbdsp\\core.db"
logger = logging.getLogger(__name__)


class BBoxImpl(DBModel):
    def __init__(self, _id,x=None,y=None, width=None, height=None):
        super().__init__(_id, ROOT_DB, "bbox")
        if self.get_id() is not None:
            data = self.get()
            self.x = data[0]["x"]
            self.y = data[0]["y"]
            self.width = data[0]["width"]
            self.height = data[0]["height"]
        else:
            self.width = width
            self.height = height
            self.x = x
            self.y = y

    @property
    def top_left(self):
        return Point(self.x, self.y)
    
    @property
    def bottom_right(self):
        return Point(self.x + self.width, self.y + self.height)

    def delete(self):
        pass

    def save(self):
        statement = f"INSERT OR REPLACE INTO {self.table_name} (_id, x, y, width, height) VALUES(?,?,?,?,?)"
        args = (self.get_id(), self.top_left.x, self.top_left.y, self.width, self.height)
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)


class ArgImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "arg")
        self.name = None
        self.value = None

    # CRUD Operations
    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self._id}"
        return core_db.execute_query(self.db_host, statement)

    def delete(self):
        pass

    def save(self):
        statement = f"INSERT OR REPLACE into {self.table_name} " \
                    + f"(_id, arg_name, arg_value) " \
                    + f"VALUES(?,?,?) " \
                    + f"RETURNING *"
        args = (self._id, self.name, self.value)
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)


class ArgEntryImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "arg_entry")
        self.secondary_table = "arg_link"
        self.args = None
        self.name = None

    # CRUD Operations

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self._id}"
        return core_db.execute_query(self.db_host, statement)

    def get_all_args(self):
        statement = f"SELECT * FROM {self.secondary_table} WHERE arg_entry_id  = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)

    def save(self):
        if self.get_id() is None:
            logger.debug(f"Creating ID for new arg_entry {self.name}")
            statement = f"INSERT OR REPLACE INTO {self.table_name} (_id, name) VALUES(?,?) RETURNING *"
            args = (self.get_id(), self.name)
            resp = core_db.execute_query(self.db_host, statement, args)
            self.new_id_from_db(resp)

        for arg in self.args:
            arg.save()
            statement = f"INSERT OR REPLACE INTO {self.secondary_table} (arg_entry_id, arg) VALUES(?,?) RETURNING *"
            resp = core_db.execute_query(self.db_host, statement, (self.get_id(), arg.get_id()))

    def delete(self):
        pass


class LocationImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "location")
        self.location_name = None

    def delete(self):
        pass

    def save(self):
        statement = f"INSERT OR REPLACE INTO {self.table_name} (_id, location_name) VALUES(?,?) RETURNING *"
        args = (self.get_id(), self.location_name)
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)


class NodeImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "node")
        self.x_off = None
        self.y_off = None
        self.reference = None
        self.location = None

    def delete(self):
        pass

    def save(self):
        self.reference.save()
        l_id = self.location.get_id() if self.location is not None else None
        statement = f"INSERT OR REPLACE INTO {self.table_name} " \
                    + f"(_id, location, x_off, y_off, reference) VALUES(?,?,?,?,?) RETURNING *"
        args = (self.get_id(), l_id, self.x_off, self.y_off, self.reference.get_id())
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)


    def get(self):
        pass


class TaskImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "task")

    def delete(self):
        pass

    def save(self):
        pass

    def get(self):
        pass


class StepImpl(DBModel):
    def delete(self):
        pass

    def save(self):
        pass

    def get(self):
        pass

    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "step")


class ReferenceTypeImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "reference_type")
        self.name = None

    def delete(self):
        pass

    def save(self):
        statement = f"INSERT OR REPLACE INTO {self.table_name} (_id, reference_type_name) VALUES(?,?) RETURNING *"
        args = (self.get_id(), self.name)
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)

    def get_by_name(self):
        statement = f"SELECT * FROM {self.table_name} WHERE reference_type_name = '{self.name}'"
        return core_db.execute_query(self.db_host, statement)


class ReferenceImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "reference")
        self.image_process = None
        self.bbox = None
        self.args = None
        self.reference_type = None

    def delete(self):
        pass

    def save(self):
        # Save preqs
        if self.reference_type is not None:
            self.reference_type.save()
        statement = f"INSERT OR REPLACE INTO {self.table_name} " \
                    + f"(_id, reference_type, arg_entry, bbox) VALUES(?,?,?,?) RETURNING *"
        bbox_id = self.bbox.get_id() if self.bbox is not None else None
        args = (self.get_id(), self.reference_type.get_id(), self.args.get_id(), bbox_id)
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)


class ImageProcessImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "image_process")
        self.args = None
        self.name = None

    def delete(self):
        pass

    def save(self):
        statement = f"INSERT OR REPLACE INTO {self.table_name} (_id, name, arg_entry) VALUES(?,?,?) RETURNING *"
        args = (self.get_id(), self.name, self.args.get_id())
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)
        self.args.save()

    def get(self):
        statement = f"SELECT * FROM {self.table_name} WHERE _id = {self.get_id()}"
        return core_db.execute_query(self.db_host, statement)

    @staticmethod
    def get_all():
        statement = f"SELECT * FROM image_process"
        data = core_db.execute_query(ROOT_DB, statement)
        resp = {}
        for entry in data:
            from Client.models.core import ImageProcess
            resp[entry["name"]] = ImageProcess(entry["_id"])
        return resp
