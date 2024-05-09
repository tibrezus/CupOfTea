import grpc
import json
from dapr.proto import common_v1
from dapr.proto import dapr_pb2_grpc
from google.protobuf.any_pb2 import Any

def run():
    # Open a gRPC channel
    with grpc.insecure_channel('localhost:50001') as channel:
        # Create a stub (client)
        stub = dapr_pb2_grpc.DaprStub(channel)

        # Create a new InvokeServiceRequest
        agent_data = {
            "name": "Antoain Jelliu",
            "description": "A metaphysics nerd.",
            "tea_amount_ml": 100
        }
        message_data = {
            "agent": agent_data,
            "message": "As I sip my tea, I ponder on the intricacies of metaphysics."
        }
        request_data = json.dumps(message_data).encode('utf-8')
        invoke_service_request = common_v1.InvokeRequest(method='generate', data=Any(value=request_data))

        # Prepare the metadata for Dapr App Id
        metadata = (('dapr-app-id', 'dialogue-generator'),)

        # Make the call
        response = stub.InvokeService(common_v1.InvokeServiceRequest(id='dialogue-generator', message=invoke_service_request), metadata=metadata)

        # Print response
        print("Received: " + response.data.value.decode())

if __name__ == '__main__':
    run()
