import json
import math
import requests
from app.core.bert.bert_extract_feature import convert_sequence_to_features
from app.core.constants import BertServingTask


def serve(sequences, serving_url, max_seq_length, batch_size=32, task=BertServingTask.CLASSIFICATION, is_sequence_pair=False):
    features = convert_sequence_to_features(sequences, max_seq_length, task, is_sequence_pair)
    instances = [
        {
            'input_ids': f.input_ids,
            'input_mask': f.input_mask,
            'segment_ids': f.segment_ids,
            'label_ids': f.label_ids
        } for f in features
    ]
    num_batches = math.ceil(len(instances) / batch_size)
    responses = []
    for i in range(num_batches):
        data = json.dumps({
            'signature_name': 'serving_default',
            'instances': instances[i * batch_size: min(len(instances), (i + 1) * batch_size)]
        })
        batch_response = requests.post(serving_url, data=data, headers={'content-type': 'application/json'})
        responses.append(batch_response)
    if any([r.status_code != 200 for r in responses]):
        # TODO
        #   输出日志详情
        print(responses[0].text)
        return []
    predictions = []
    for r in responses:
        batch_predictions = json.loads(r.text)['predictions']
        predictions.extend(batch_predictions)
    return predictions
