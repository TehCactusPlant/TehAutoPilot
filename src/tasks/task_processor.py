from src.data.bank import DataBank
from src.database.core import DBInterface
from src.imaging.processing import ImageProcessor
from src.navigation.nodes import NodeMapping
from src.tasks.steps.steps import Step
from src.tasks.task import Task
import sqlite3 as db
import logging
logger = logging.getLogger(__name__)


class TaskAssembler:
    # Steps and Tasks DB
    def __init__(self, db_name):
        self.sql_con = db.connect(db_name)
        self.db_interface = DBInterface()

    def assemble_task(self, task_id) -> Task:
        pass

    def assemble_step(self, step_id) -> Step:
        step_data = self.db_interface.assemble_step_by_id(step_id)

    def print_all_tasks(self):
        logger.info("Available Tasks to register: ")
        for name, t_id in self.all_task_names.items():
            logger.debug(f"{t_id} {name}")


class TaskProcessor:
    def __init__(self, assembler: TaskAssembler,
                 node_navigator: NodeMapping,
                 img_processor: ImageProcessor) -> None:
        self.current_area = ""
        self.current_task: Task = None
        self.tasks: list[Task] = []
        self.node_navigator = node_navigator
        self.assembler = assembler
        self.img_processor = img_processor
        self.data_bank = DataBank()

    def _add_task(self, task: Task):
        self.tasks.append(task)

    def _interrupt_task(self, new_task: Task):
        if self.current_task.should_restart:
            self.current_task.restart()
        self.tasks.insert(0, new_task)
        self.current_task = new_task


    def _complete_task(self):
        last_task = self.tasks.pop(0)
        logger.info(f"Task complete: {last_task.name}")
        self.current_task = self.tasks[0]

    def _run_task(self):
        pass

    def start_task(self, task_name):
        task_id = self.assembler.all_task_names[task_name]
        if task_id is not None:
            task = self.assembler.assemble_task(task_id)
            self._interrupt_task(task)
        else:
            logger.error(f"Task name {task_name} does not exist as a task")

    def add_task(self, task_name):
        task_id = self.assembler.all_task_names[task_name]
        if task_id is not None:
            task = self.assembler.assemble_task(task_id)
            self._add_task(task)
        else:
            logger.error(f"Task name {task_name} does not exist as a task")

    def complete_task(self):
        self._complete_task()

