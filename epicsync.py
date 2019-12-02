import sys
import json
import yaml
import hmac
import hashlib

import requests
from flask import Flask, request, abort

app = Flask(__name__)

with open('config.yaml', 'r') as yamlfile:
    config = yaml.safe_load(yamlfile)

GITHUB_TOKEN = config.get('token')
ENTITY_PREFIX_MAP = config.get('entity_prefix_map')
TARGET_REPOS = config.get('target_repos')

WEBHOOK_SECRET = config.get('webhook_secret').encode()

class Label:
    URL = 'https://api.github.com'

    def __init__(self, token):
        self._token = token

    def _get_headers(self):
        return {
            'authorization': 'token %s' % self._token
        }

    def _label(self, prefix, number):
        return '%s:%s' % (prefix, number)

    def _truncate_description(self, description):
        if len(description) >= 100:
            return description[:99] + '…'
        else:
            return description

    def get(self, repo, prefix, number):
        label = self._label(prefix, number)
        response = requests.get(self.URL + '/repos/%s/labels/%s' % (repo, label),
                                headers=self._get_headers())

        if response.status_code == 404:
            return None
        else:
            return response.json()

    def post(self, repo, prefix, number, color='e5e5e5', description=None):
        if len(description) >= 100:
            description = description[:99] + '…'

        body = {
            'name': self._label(prefix, number),
            'description': self._truncate_description(description),
            'color': color
        }
        response = requests.post(self.URL + '/repos/%s/labels' % repo,
                                 headers=self._get_headers(),
                                 json=body)

        if response.status_code != 201:
            raise Exception('Unable to create label')

    def update(self, repo, prefix, number, color=None, description=None):
        body = {}
        if description:
            body['description'] = self._truncate_description(description)
        if color:
            body['color'] = color

        label = self._label(prefix, number)

        response = requests.patch(self.URL + '/repos/%s/labels/%s' % (repo, label),
                                  headers=self._get_headers(),
                                  json=body)

        if response.status_code != 200:
            raise Exception('Unable to modify label')

    def upsert(self, repo, prefix, number, color=None, description=None):
        existing_label = self.get(repo, prefix, number)
        if not existing_label:
            self.post(repo, prefix, number, color, description)
        elif ((existing_label.get('description') != description) or
                (existing_label.get('color') != color)):
            self.update(repo, prefix, number, color, description)

    def delete(self, repo, prefix, number):
        label = self._label(prefix, number)

        response = requests.delete(self.URL + '/repos/%s/labels/%s' % (repo, label),
                                   headers=self._get_headers())

LABELER = Label(GITHUB_TOKEN)

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

    prefix = ENTITY_PREFIX_MAP.get(entity_type)

    number = event.get(entity_type).get('number')
    title = event.get(entity_type).get('title')

    print('Processing:', headers.get('X-Github-Delivery'),
          event.get('action'), entity_type, prefix, number, title, file=sys.stderr)

    if event.get('action') in ['opened', 'edited', 'created']:
        for repo in TARGET_REPOS:
            LABELER.upsert(repo, prefix, number, color='b4f291', description=title)

    elif event.get('action') == 'deleted':
        for repo in TARGET_REPOS:
            LABELER.delete(repo, prefix, number)

    return 'OKAY'

if __name__ == "__main__":
    app.run()
