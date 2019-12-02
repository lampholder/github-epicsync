import sys
import requests

class Labeler:
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
        elif response.ok:
            return response.json()
        else:
            raise Exception('%d:%s' % (response.status_code, response.text))

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
            print(response.url, response.status_code, response.text, file=sys.stderr)
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
