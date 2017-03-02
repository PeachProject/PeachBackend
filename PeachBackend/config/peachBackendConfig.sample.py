##########################################
##########################################
###### MANDATORY CONFIG SETTINGS #########
##########################################
##########################################

peach_shared_path = "<current_git>/PeachShared"

schemas = {
    "workflow":"<current_git>/PeachShared/schemas/workflow.avsc"
}

queue_path = "<local_queue_temp>"

service_hub_path = "<Peach_Service_Hub>"

servers = {
"kafka": "<Kafka_Server>"
}

mysql_info = {
    "host": "<mysql_host>",
    "user": "<mysql_user>",
    "password": "<mysql_pw>",
    "database": "<mysql_database>"
}

##########################################
##########################################
###### Secondary CONFIG SETTINGS #########
##########################################
##########################################

logfile = "backendlog"

events = {
"workflow_execute-workflow":"Workflow_ExecuteWorkflow",
"Service_serviceListUpdated":"Service_serviceListUpdated",
"workflow_workflow-processed":"Workflow_WorkflowProcessed",
}


table_names = {
    "queue":  "queue",
    "generated_data_files": "generated_data_files"
}

##########################################
##########################################
####### Don't change this part! ##########
##########################################
##########################################

def get_schema_path(id):
    return schemas.get(id)

def get_queue_path():
    return queue_path

def get_service_hub_path():
    return service_hub_path

def get_library_path():
    return peach_shared_path

def get_event(id):
    return events.get(id)

def get_server_address(id):
    return servers.get(id)

import logging

def get_logfile_path():
    return logfile

def get_level():
    return logging.INFO

def get_mysql_info():
    return mysql_info

def get_table(key):
    return table_names[key]
