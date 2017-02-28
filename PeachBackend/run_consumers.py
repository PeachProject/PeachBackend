
import config.peachBackendConfig as Config
import consumers.workflow_consumer as WorkflowConsumer
import consumers.process_workflows_consumer as ProcessWorkflowsConsumer
import os
from subprocess import call



if __name__ == '__main__':
    workflow_schema = Config.get_schema_path("workflow")
    kafka_server = Config.get_server_address("kafka")
    queue_path = Config.get_queue_path()
    service_hub_path = Config.get_service_hub_path()
    library_path = Config.get_library_path()

    import argparse
    parser = argparse.ArgumentParser(description='Starts all consumers')
    parser.add_argument("-consumer", "--c", type=str, help="Which consumer? (0 means all, 1 means workflow_consumer ...)")
    args = parser.parse_args()
    if args.c == "1":
        WorkflowConsumer.start(kafka_server, workflow_schema, queue_path, service_hub_path, library_path)
    elif args.c == "2":
        ProcessWorkflowsConsumer.start(kafka_server, queue_path)
    else:
        for i in range(1, 3):
            cmd = "python " + os.path.dirname(os.path.realpath(__file__)) + "/run_consumers.py --c " + str(i)
            gnome_cmd = ["gnome-terminal", "-x", "sh", "-c", "\"" + cmd + "\"", ]
            raw = " ".join(gnome_cmd)
            call(raw, shell=True)
            print raw