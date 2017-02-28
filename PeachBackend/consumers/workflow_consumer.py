import io
import logging
import avro.schema
import avro.io
import json
from kafka import KafkaConsumer
import config.peachBackendConfig as Config
import workflow_generators.dask_script_generator as DaskScriptGenerator
from config.peachBackendConfig import get_level
from config.peachBackendConfig import get_logfile_path
from config.peachBackendConfig import get_mysql_info
from config.peachBackendConfig import get_table
from logfactory.factory import LoggerFactory
import mysql.connector
import hashlib
import time
import os
import datetime
from kafka import KafkaProducer


def start(kafka_server_address, workflow_schema_path, queue_path, service_hub_path, library_path):
  #Logging
  logFactory = LoggerFactory(get_level(), get_logfile_path())
  log = logFactory.get_logger()
  log.setLevel(logging.INFO)
  logfile = logging.FileHandler("backendlog")
  log.addHandler(logfile)
  print("Workflow consumer started... " + "using workflow schema located at: " + workflow_schema_path)
  #Kafka
  event = Config.get_event("workflow_execute-workflow")
  consumer = KafkaConsumer(event, bootstrap_servers=kafka_server_address)
  #Avro
  schema = avro.schema.parse(open(workflow_schema_path).read())
  #Infinity loop that consumes workflow execution events
  for msg in consumer:
    print("Received workflow execution message")
    try:
        print("Parsing received workflow")
        bytes_reader = io.BytesIO(msg.value)
        decoder = avro.io.BinaryDecoder(bytes_reader)
        reader = avro.io.DatumReader(schema)
        workflow = reader.read(decoder)
        
        filename = workflow["user"] + "_" + hashlib.md5(msg.value).hexdigest() + "_" + str(time.time()).replace(".", "_") + ".py"
        path = os.path.join(queue_path, filename)

        print("Creating mysql entry")

        mysql_info = get_mysql_info()
        try:
            cnx = mysql.connector.connect(**mysql_info)
            x = cnx.cursor()
            table = get_table("queue")
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            #TODO: Set priority dynamically somehow
            query = "INSERT INTO {} VALUES (NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
                table,
                workflow["user"],
                filename,
                json.dumps(workflow),
                "0",
                "0",
                "still unknown #todo",
                timestamp,
                "",
                "1",
                ""
            )
            try:
                x.execute(query)
                queue_index = x.lastrowid
                cnx.commit()
                print(">>> Successfully created mysql entry")

               
            except Exception as e:
                cnx.rollback()
                print(">>> Error when inserting row" + str(e))
            
        except mysql.connector.Error as err:
            print(">>> MYSQL error ({})".format(err))
        else:
            cnx.close()
        
        print(">>> Successfully parsed received workflow")
        print("Generating dask script")
        dsk_script_str = DaskScriptGenerator.generate_dask_script(workflow, service_hub_path, library_path, queue_index)
        print("Saving dask script")

        with open(path, "w") as text_file:
            text_file.write(dsk_script_str)
        
        print(">>> Successfully generated dask script to {}".format(path))

        producer = KafkaProducer(bootstrap_servers=kafka_server_address)
        topic = Config.get_event("workflow_workflow-processed")
        producer.send(topic, str(queue_index))

        producer.flush()

    except Exception as e:
        print(str(e))
    
    print("-------- Finished --------")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='This script should be used to start a kafka consumer that receives a workflow and processes it (dask script generation etc.)')
    parser.add_argument("-kafkaaddress", "--ka", type=str, help="The address to the kafka server that forwards the event.")
    parser.add_argument("-queuepath", "--q", type=str, help="The path to the folder where all the dask scripts will be")
    parser.add_argument("-workflowschema", "--wf", type=str, help="The path to the workflow schema")
    parser.add_argument("-servicehub", "--sh", type=str, help="The service hub path")
    args = parser.parse_args()
    start(args.ka, args.wf, args.q, args.sh)