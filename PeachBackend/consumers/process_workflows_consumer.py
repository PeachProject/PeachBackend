from logfactory.factory import LoggerFactory
from kafka import KafkaConsumer
import config.peachBackendConfig as Config
import logging
from config.peachBackendConfig import get_level
from config.peachBackendConfig import get_logfile_path
from config.peachBackendConfig import get_mysql_info, get_table
import mysql.connector
import os
import subprocess

def start(kafka_server_address, queue_path):
    logFactory = LoggerFactory(get_level(), get_logfile_path())
    log = logFactory.get_logger()
    log.setLevel(logging.INFO)
    logfile = logging.FileHandler("backendlog")
    log.addHandler(logfile)

    event = Config.get_event("workflow_workflow-processed")
    consumer = KafkaConsumer(event, bootstrap_servers=kafka_server_address)

    for msg in consumer:
        try:
            print("Received processed workflow")
            primary_key = msg.value
            mysql_info = get_mysql_info()
            try:
                cnx = mysql.connector.connect(**mysql_info)
                x = cnx.cursor()
                table = get_table("queue")
                #TODO: Set priority dynamically somehow
                query = "SELECT * FROM {} WHERE id = {}".format(table, str(int(primary_key)))
                try:
                    x.execute(query,)
                    for (id, user, execution_file, workflow_json, status, progress, original_workflow_file, sending_date, finished_date, priority, output_file) in x:
                        file_path = os.path.join(queue_path, execution_file)
                        raw = "python '{}' &".format(file_path)
                        print raw
                        proc = subprocess.call(raw, shell=True) #maaaagic
                    x.close()
                    cnx.close()
                    print(">>> Successfully started process")
                except Exception as e:
                    cnx.rollback()
                    print(">>> Error when inserting row " + str(e))
                
            except mysql.connector.Error as err:
                print(">>> MYSQL error ({})".format(err))
            else:
                cnx.close()
        except Exception as e:
            print(str(e))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='This script should be used to start a kafka consumer that receives a processed workflow and executes it in a new subprocess.')
    parser.add_argument("-kafkaaddress", "--ka", type=str, help="The address to the kafka server that forwards the event.")
    parser.add_argument("-queuepath", "--q", type=str, help="The path to the folder where all the dask scripts will be")
    args = parser.parse_args()
    start(args.ka, args.q)