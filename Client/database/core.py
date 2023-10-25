import os

import coloredlogs

from Client.database.models import *
from Client.models.core import *

logger = logging.getLogger(__name__)


class DBInterface:
    DB_PATH = "C:\\Users\\Cactus\\Documents\\pkmnbdsp\\core.db"
    IMAGES_PATH = "C:\\Users\\Cactus\\Documents\\pkmnbdsp\\images"
    CONTOURS_PATH = "C:\\Users\\Cactus\\Documents\\pkmnbdsp\\contours"

    def create_tables(self):
        # Standalone Entities
        logger.info("Creating Database tables")
        tables = []

        tables.append(Table("arg_entry", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("name", ColumnType.TEXT, is_unique=True)
        ]))

        tables.append(Table("arg", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("arg_name", ColumnType.TEXT),
            Column("arg_value", ColumnType.BLOB)
        ]))

        tables.append(Table("arg_link", [
            Column("arg_entry_id", ColumnType.INTEGER, co_unique=True,
                   foreign_key=ForeignKey("arg_entry", "_id")),
            Column("arg", ColumnType.INTEGER, co_unique=True,
                   foreign_key=ForeignKey("arg", "_id"))
        ]))

        tables.append(Table("bbox", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("x", ColumnType.INTEGER),
            Column("y", ColumnType.INTEGER),
            Column("width", ColumnType.INTEGER),
            Column("height", ColumnType.INTEGER)
        ]))

        tables.append(Table("step_type", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("type_name", ColumnType.TEXT)
        ]))

        tables.append(Table("task", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("task_name", ColumnType.TEXT),
            Column("arg_entry_id", ColumnType.INTEGER,
                   foreign_key=ForeignKey("arg_entry", "_id")),
            Column("should_restart", ColumnType.INTEGER)
        ]))

        tables.append(Table("location", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("location_name", ColumnType.TEXT, is_unique=True)
        ]))

        tables.append(Table("step", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("step_name", ColumnType.TEXT),
            Column("step_type", ColumnType.INTEGER,
                   foreign_key=ForeignKey("step_type", "_id")),
            Column("arg_entry", ColumnType.INTEGER,
                   foreign_key=ForeignKey("arg_entry", "_id")),
            Column("positive_response", ColumnType.INTEGER,
                   foreign_key=ForeignKey("step", "_id")),
            Column("negative_response", ColumnType.INTEGER,
                   foreign_key=ForeignKey("step", "_id"))
        ]))

        tables.append(Table("image_process", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("name", ColumnType.TEXT, is_unique=True),
            Column("arg_entry", ColumnType.INTEGER,
                   foreign_key=ForeignKey("arg_entry", "_id"))
        ]))

        tables.append(Table("reference_type",[
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("reference_type_name", ColumnType.TEXT, is_unique=True)
        ]))

        tables.append(Table("reference", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("name", ColumnType.TEXT, is_unique=True),
            Column("reference_type", ColumnType.INTEGER,
                   foreign_key=ForeignKey("reference_type", "_id")),
            Column("arg_entry", ColumnType.INTEGER,
                   foreign_key=ForeignKey("arg_entry", "_id")),
            Column("bbox", ColumnType.INTEGER,
                   foreign_key=ForeignKey("bbox", "_id")),
            Column('image_process', ColumnType.INTEGER,
                   foreign_key=ForeignKey("image_process", "_id")),
        ]))

        tables.append(Table("node", [
            Column("_id", ColumnType.INTEGER, primary_key=True),
            Column("location", ColumnType.INTEGER,
                   foreign_key=ForeignKey("location", "_id")),
            Column("x_off", ColumnType.INTEGER),
            Column("y_off", ColumnType.INTEGER),
            Column("reference", ColumnType.INTEGER,
                   foreign_key=ForeignKey("reference", "_id")),
        ]))

        tables.append(Table("node_link", [
            Column("node1", ColumnType.INTEGER, co_unique=True,
                   foreign_key=ForeignKey("node", "_id")),
            Column("node2", ColumnType.INTEGER, co_unique=True,
                   foreign_key=ForeignKey("node", "_id")),
            Column("distance", ColumnType.INTEGER),
            Column("direction", ColumnType.REAL)
        ]))

        tables.append(Table("task_step_link", [
            Column("step_number", ColumnType.INTEGER),
            Column("task", ColumnType.INTEGER,
                   foreign_key=ForeignKey("task", "_id")),
            Column("step", ColumnType.INTEGER,
                   foreign_key=ForeignKey("step", "_id"))
        ]))

        for table in tables:
            table.create_table(self.DB_PATH)

        # Create File paths
        os.mkdir(self.CONTOURS_PATH)
        os.mkdir(self.IMAGES_PATH)


    def open_connection(self):
        con = db.connect(self.DB_PATH)
        cur = con.cursor()
        return con, cur

    def close_connection(self, con, cur):
        cur.close()
        con.close()


# Tests
def create_debug_values():
    db_con = DBInterface()
    # Debug Values - Forcibly create entries to ensure MAX works as expected
    debug_arg_id = db_con.write_arg("DEBUG_KEY", "DEBUG_VALUE")
    debug_args_id = db_con.write_arg_entry(1, debug_arg_id)
    db_con.write_function_arg(1, "DEBUG_FUNCTION_ARG")


def object_tests():
    db_con = DBInterface()
    # Test / Location 1
    test_location = Location(None, "solaceon")
    test_location.save()  # Creates new ID
    logger.info(f"Location ID: {test_location.get_id()}")
    assert test_location.get_id() is not None
    test_location = Location(1)
    logger.info(f"Location ID: {test_location.get_id()} for location {test_location.location_name}")

    preset_name = "Blue Door"
    im_proc: ImageProcess = ImageProcess(None, preset_name, None)
    im_proc.args = ArgEntry(None, "Blue Door")
    int_hsv_min = (81,127,130)
    int_hsv_max = (112,255,255)
    im_proc.args.add_arg(Arg(None, "h_min", int_hsv_min[0]))
    im_proc.args.add_arg(Arg(None, "s_min", int_hsv_min[1]))
    im_proc.args.add_arg(Arg(None, "v_min", int_hsv_min[2]))
    im_proc.args.add_arg(Arg(None, "h_max", int_hsv_max[0]))
    im_proc.args.add_arg(Arg(None, "s_max", int_hsv_max[1]))
    im_proc.args.add_arg(Arg(None, "v_max", int_hsv_max[2]))
    im_proc.save()

    preset_name = "Brown Door"
    im_proc: ImageProcess = ImageProcess(None, preset_name, None)
    im_proc.args = ArgEntry(None, "Brown Door")
    int_hsv_min = (10, 53, 81)
    int_hsv_max = (22, 53, 209)
    im_proc.args.add_arg(Arg(None, "h_min", int_hsv_min[0]))
    im_proc.args.add_arg(Arg(None, "s_min", int_hsv_min[1]))
    im_proc.args.add_arg(Arg(None, "v_min", int_hsv_min[2]))
    im_proc.args.add_arg(Arg(None, "h_max", int_hsv_max[0]))
    im_proc.args.add_arg(Arg(None, "s_max", int_hsv_max[1]))
    im_proc.args.add_arg(Arg(None, "v_max", int_hsv_max[2]))
    im_proc.save()

    ref_type = ReferenceType(None, "hsv contour")
    ref_type.save()

    assert im_proc.get_id() is not None
    assert ref_type.get_id() is not None


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    coloredlogs.install(level="DEBUG", logger=logger)
    WIPE = True
    logger.info("Starting databasing")
    db_base_con = DBInterface()
    if WIPE:
        logger.info("Deleting Database and restoring")
        try:
            os.remove(db_base_con.DB_PATH)
            os.removedirs(db_base_con.CONTOURS_PATH)
            os.removedirs(db_base_con.IMAGES_PATH)
        except Exception as e:
            logger.error(e)
        db_base_con.create_tables()
        object_tests()
