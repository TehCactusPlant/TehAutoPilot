import logging

from Client.common_utils.models import Point
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

    @staticmethod
    def get_all():
        statement = f"SELECT _id FROM location"
        resp = core_db.execute_query(ROOT_DB, statement)
        from Client.models.core import Location
        locations = []
        for row in resp:
            locations.append(Location(row["_id"]))
        return locations


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
        self.location.save()
        l_id = self.location.get_id() if self.location is not None else None
        statement = f"INSERT OR REPLACE INTO {self.table_name} " \
                    + f"(_id, location, x_off, y_off, reference) VALUES(?,?,?,?,?) RETURNING *"
        args = (self.get_id(), l_id, self.x_off, self.y_off, self.reference.get_id())
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)
        print(f"New ID for node: {self.get_id()}")

    def get(self):
        statement = f"SELECT * FROM node WHERE _id = {self.get_id()}"
        resp = core_db.execute_query(self.db_host, statement)
        if len(resp) > 0:
            return resp[0]

    @staticmethod
    def get_all_in_location(location):
        statement = f"SELECT * FROM node WHERE location = {location.get_id()}"
        resp = core_db.execute_query(ROOT_DB, statement)
        nodes = {}
        from Client.models.core import ReferenceBuilder
        from Client.models.core import Node
        for row in resp:
            ref_class = ReferenceBuilder.assemble_by_type(row["reference_type"])
            if ref_class is not None:
                ref = ref_class(row["image_reference"])
                nodes[row["_id"]] = Node(row["_id"], location, row["x_off"], row["y_off"], ref)
        return nodes


class NodeLinkImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "node_link")
        self.node1 = None
        self.node2 = None
        self.dir_vector = None

    def delete(self):
        pass

    def save(self):
        statement = "INSERT OR IGNORE INTO node_link (node1, node2, distance, direction) VALUES(?,?,?,?)"
        args = (self.node1.get_id(), self.node2.get_id(), self.dir_vector.direction, self.dir_vector.magnitude)
        resp = core_db.execute_query(self.db_host, statement, args)
        return resp

    def get(self):
        pass

    @staticmethod
    def get_multiple(node_ids):
        nodes_ids = tuple(node_ids)
        statement = f"SELECT * FROM node_link WHERE node1 IN {node_ids} OR node2 in {node_ids}"
        resp = core_db.execute_query(ROOT_DB, statement)
        links = []
        for row in resp:
            from Client.models.core import NodeLink
            from Client.navigation.nodes import NodeMapping
            mapper = NodeMapping()
            node1 = mapper.loaded_nodes(row["node1"])
            node2 = mapper.loaded_nodes(row["node2"])
            links.append(NodeLink(None, node1, node2, row["distance"], row["direction"]))
        return links


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

    @staticmethod
    def get_all():
        statement = "SELECT * FROM reference_type"
        resp = core_db.execute_query(ROOT_DB, statement)
        types = []
        for row in resp:
            from Client.models.core import ReferenceType
            types.append(ReferenceType(row["_id"]))
        return types


class ReferenceImpl(DBModel):
    def __init__(self, _id):
        super().__init__(_id, ROOT_DB, "reference")
        self.image_process = None
        self.bbox = None
        self.args = None
        self.reference_type = None
        self.reference_data = None
        self.name = None

    def delete(self):
        pass

    def save(self):
        # Save pre-reqs
        if self.reference_type is not None:
            self.reference_type.save()
        if self.image_process is not None:
            self.image_process.save()
        # Save object
        statement = f"INSERT OR REPLACE INTO {self.table_name} " \
                    + f"(_id, reference_type, arg_entry, bbox, name, image_process) VALUES(?,?,?,?,?,?) RETURNING *"
        bbox_id = self.bbox.get_id() if self.bbox is not None else None
        arg_id = self.args.get_id() if self.args is not None else None
        args = (self.get_id(), self.reference_type.get_id(), arg_id, bbox_id, self.name, self.image_process.get_id())
        resp = core_db.execute_query(self.db_host, statement, args)
        self.new_id_from_db(resp)
        self.save_numpy(f"{self.get_id()}_{self.name}", self.reference_data)

    @staticmethod
    def get_all() -> dict:
        statement = f"SELECT _id, name, reference_type FROM reference"
        data = core_db.execute_query(ROOT_DB, statement)
        references = []
        from Client.models.core import ReferenceBuilder
        for row in data:
            r_class = ReferenceBuilder.assemble_by_type(row["reference_type"])
            references.append(r_class(row["_id"]))
        return references

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
    def get_all() -> dict:
        statement = f"SELECT * FROM image_process"
        data = core_db.execute_query(ROOT_DB, statement)
        resp = {}
        for entry in data:
            from Client.models.core import ImageProcess
            im_proc = ImageProcess(entry["_id"])
            resp[im_proc.name] = im_proc
        return resp
