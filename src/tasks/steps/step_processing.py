from src.tasks.steps.movement_steps import *
import logging
logger = logging.getLogger(__name__)


step_types = {
    "move to": MoveTo
}


def build_step(data_bank, raw_step_data: dict = None):
    if raw_step_data is None:
        return None
    step_class_name = raw_step_data["function"]["function_name"]
    step_name = raw_step_data["step_name"]
    if step_class_name is None or step_class_name not in step_types:
        logger.error(f"No step association found for function type {step_class_name} for step: {step_name}")
    else:
        args = raw_step_data.get(raw_step_data)
        condition_step = build_step(data_bank, raw_step_data["step_condition"])
        positive_step = build_step(data_bank, raw_step_data["sc_positive_step"])
        negative = build_step(data_bank, raw_step_data["sc_negative_step"])
        "sc_positive_step"
        step = step_types[step_class_name](data_bank, args, condition_step, positive_step, negative)
        return step
