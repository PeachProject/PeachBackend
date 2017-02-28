import io, random
import avro.schema
from avro.io import DatumWriter
from kafka import KafkaProducer

def send(kafka_server_address, workflow_schema_path, kafka_topic):

    schema = avro.schema.parse(open(workflow_schema_path, "rb").read())

    producer = KafkaProducer(bootstrap_servers=kafka_server_address)
    topic = kafka_topic

    writer = avro.io.DatumWriter(schema)
    bytes_writer = io.BytesIO()
    encoder = avro.io.BinaryEncoder(bytes_writer)
    #
    #
    #    [A_out_0]-----[B_in_0] [B] [B_out_0]-----[D_in_0]
    # [A]                                                 [D]
    #    [A_out_1]-----[C_in_0] [C] [C_out_0]-----[D_in_1]
    #

    writer.write({
    "nodes": [
        {
            "id": "node_0",
            "service": {
                "id": "DoseCalc",
                "version": 1
            },
            "parameters": [0],
            "connections": [{
                "port_idx": -1,
                "node_id": "filepath"
            },
            {
                "port_idx": -1,
                "node_id": "filepath"
            }
            ]
        },
        {
            "id": "node_1",
            "service": {
                "id": "DoseCalc",
                "version": 1
            },
            "parameters": [0],
            "connections": [{
                "port_idx": 0,
                "node_id": "node_0"
            },
            {
                "port_idx": -1,
                "node_id": "filepath"
            }]
        }
    ],
    "name": "DAG",
    "user": "muessema@ad"
}, encoder)

    raw_bytes = bytes_writer.getvalue()
    for i in range(0, 10):
        producer.send(topic, raw_bytes)
        producer.flush()
    producer.close()
