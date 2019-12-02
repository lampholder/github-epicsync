import sys
import json
import yaml
import hmac
import hashlib

import requests
from flask import Flask, request, abort

from labeler import Labeler

app = Flask(__name__)

with open('config.yaml', 'r') as yamlfile:
    config = yaml.safe_load(yamlfile)

GITHUB_TOKEN = config.get('github_token')
ENTITY_LABEL_CONFIG = config.get('entity_label_config')
TARGET_REPOS = config.get('target_repos')

WEBHOOK_SECRET = config.get('webhook_secret').encode()

LABELER = Labeler(GITHUB_TOKEN)

def request_signature_is_valid(shared_secret, request):
    signature = request.headers.get('X-Hub-Signature')

    hmac_gen = hmac.new(shared_secret, request.data, hashlib.sha1)
    digest = "sha1=" + hmac_gen.hexdigest()

    return signature == digest

@app.route('/', methods=['POST'])
def handle_request():
    if not request_signature_is_valid(WEBHOOK_SECRET, request):
        print('Invalid request signature', file=sys.stderr)
        abort(400)

    headers = request.headers
    event = request.json

    event_type = headers.get('X-Github-Event')
    if event_type == 'issues':
        entity_type = 'issue'
    elif event_type == 'milestone':
        entity_type = 'milestone'

    label = ENTITY_LABEL_CONFIG.get(entity_type)

    number = event.get(entity_type).get('number')
    title = event.get(entity_type).get('title')

    print('Processing:', headers.get('X-Github-Delivery'),
          event.get('action'), entity_type, label.get('prefix'),
          number, title, file=sys.stderr)

    if event.get('action') in ['opened', 'edited', 'created']:
        for repo in TARGET_REPOS:
            LABELER.upsert(repo, label.get('prefix'), number, 
                    color=label.get('color'), description=title)

    elif event.get('action') == 'deleted':
        for repo in TARGET_REPOS:
            LABELER.delete(repo, label.get('prefix'), number)

    return 'OKAY'

if __name__ == "__main__":
    app.run()
