import io
import avro.schema
from avro.io import DatumWriter, DatumReader
from avro.datafile import DataFileReader
from kafka import KafkaProducer
import schedule
import argparse
import service_list_generator as ServiceListGenerator

def send(kafka_server, schema_path, kafka_topic, service_config_paths):
    """
    Sends the services
    @param kafka_server as string to the kafka server (e.g. 172.29.1.71)
    @param schema_path as filepath to the schema (e.g. /home/user/schemata/schema.avsc)
    @param kafka_topic as string to specifiy the topic (e.g. Workflow_GetWorkflowStatus)
    @param service_config_paths
    """
    schema = avro.schema.parse(open(schema_path, "rb").read())
    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    for cfg in service_config_paths:
        reader = DataFileReader(open(cfg, "rb"), DatumReader())
        for r in reader:
            writer.write(r, encoder)

    producer = KafkaProducer(bootstrap_servers=kafka_server)
    raw_bytes = bytes_writer.getvalue()
    producer.send(kafka_topic, raw_bytes)
    producer.flush()


def update_services(directory, ignore, config_file, kafka_server, schema_path, kafka_topic):
    """
    Updates the services
    @param directory as string
    @param ignore as list of strings
    @param config_file as string
    @param kafka_server
    @param schema_path
    @param kafka_topic
    """
    service_config_paths = ServiceListGenerator.generate_service_list(directory, ignore, config_file)
    send(kafka_server, schema_path , kafka_topic, service_config_paths)

def start(directory, ignore, config_file, kafka_server, schema_path, kafka_topic, schedule_interval):
    """
    Starts the producer
    @param directory as string
    @param ignore as list of strings
    @param config_file as string
    @param kafka_server
    @param schema_path
    @param kafka_topic
    """
    if(schedule_interval):
        schedule.every(schedule_interval).minutes.do(update_services, directory, ignore, config_file, kafka_server, schema_path, kafka_topic)
        while True:
            schedule.run_pending()
    else:
        update_services(directory, ignore, config_file, kafka_server, schema_path, kafka_topic)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Produces service config list update events.')
    parser.add_argument('-d', '--directory', type=str, help="The directory where the search should be started.")
    parser.add_argument('-i', '--ignore', type=str, nargs='+', default="", help="Those directories will be ignored.")
    parser.add_argument('-c', '--config_file', type=str, default = "service.config", help="Specifies the name of the config file, e.g. service.config.")
    parser.add_argument('-k', '--kafka_server', type=str, help="Server address of kafka.")
    parser.add_argument('-sp', '--schema_path', type=str, help="Filepath of schema.")
    parser.add_argument('-kt', '--kafka_topic', type=str, help="Kakfa topic.")
    parser.add_argument('-s', '--schedule_interval', type=int, default=0, help="Update interval, will run the update every n minutes")
    args = parser.parse_args()
    start(args.directory, args.ignore, args.config_file, args.kafka_server, args.schema_path, args.kafka_topic, args.schedule_interval)
   
