from datetime import datetime
import logging
import os

class DataCollectionLogging():
# Class to implement the logging for the collection data engine.

    def __init__(self):

        # Config log file
        today = datetime.today().strftime('%Y-%m-%d')
        file_path = 'collector_logs'
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        
        filename='collector_logs/DataCollectionEngine_'+today+'.log'
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        self.log.addHandler(logging.FileHandler(filename))
        formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(message)s", "%Y-%m-%d %H:%M:%S")
        self.log.handlers[0].setFormatter(formatter)


    def log_diff_list_element (self, obj_type, obj_id, f_q_name, field, element, old_value, new_value):
    # Method to log a diff between two list objects.
        message = f"Changed object: {obj_type}, Id: {obj_id} {f_q_name}, Field: {field}, Element: {element}, Old value: {old_value}, New value: {new_value}"
        self.log.warning(message)
            
    def log_element_added (self, obj_type, obj_id, f_q_name, field, element):
    # Method to log an element added.
        message = f"Changed object: {obj_type}, Id: {obj_id} {f_q_name}, Field: {field}, Element added: {element}"
        self.log.warning(message)

    def log_element_removed (self, obj_type, obj_id, f_q_name, field, element):
    # Method to log an element removed.
        message = f"Changed object: {obj_type}, Id: {obj_id} {f_q_name}, Field: {field}, Element removed: {element}"
        self.log.warning(message)

    def log_diff_field (self, obj_type, obj_id, f_q_name, field, old_value, new_value):
    # Method to log a diff between two fields.
        message = f"Changed object: {obj_type}, Id: {obj_id} {f_q_name}, Field: {field}, Old value: {old_value}, New value: {new_value}"
        self.log.warning(message)

    def log_obj_collecting(self, obj_type, obj_name):
    # Method to log the collecting of an object.
        message = f"Collecting {obj_type} {obj_name}"
        self.log.info(message)

    def log_provider_skipped(self, provider_name):
        message = f"{provider_name} database provider skipped today."
        self.log.info(message)
