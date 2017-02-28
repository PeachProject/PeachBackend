import logging
import config.peachBackendConfig as Config
import producers.workflow_producer as WorkflowProducer
from logfactory.factory import LoggerFactory

workflow_schema = Config.get_schema_path("workflow")
kafka_server = Config.get_server_address("kafka")
event = Config.get_event("workflow_execute-workflow")
log = LoggerFactory(Config.get_level(), Config.get_logfile_path())
WorkflowProducer.send(kafka_server, workflow_schema, event)
