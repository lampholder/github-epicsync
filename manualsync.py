import sys
import json
import yaml
import hmac
import hashlib

import requests
from github import Github

from labeler import Labeler

if len(sys.argv) != 2:
    print('Usage: %s example-org/example-repo' % sys.argv[0])

SOURCE_REPO = sys.argv[1]

with open('config.yaml', 'r') as yamlfile:
    config = yaml.safe_load(yamlfile)

GITHUB_TOKEN = config.get('github_token')
ENTITY_LABEL_CONFIG = config.get('entity_label_config')
TARGET_REPOS = config.get('target_repos')

LABELER = Labeler(GITHUB_TOKEN)
github = Github(GITHUB_TOKEN)

source_repo = github.get_repo(SOURCE_REPO)

for target_repo in TARGET_REPOS:
    print('Syncing %s to %s' % (SOURCE_REPO, target_repo), file=sys.stderr)
    issue_label_config = ENTITY_LABEL_CONFIG.get('issue')
    milestone_label_config = ENTITY_LABEL_CONFIG.get('milestone')

    for issue in source_repo.get_issues():
        print('-- syncing issue \'%d:%s\'' % (issue.number, issue.title), file=sys.stderr)
        LABELER.upsert(target_repo, issue_label_config.get('prefix'),
                issue.number, issue_label_config.get('color'),
                issue.title)

    for milestone in source_repo.get_milestones():
        print('-- syncing milestone \'%d:%s\'' % (milestone.number, milestone.title), file=sys.stderr)
        LABELER.upsert(target_repo, milestone_label_config.get('prefix'),
                milestone.number, milestone_label_config.get('color'),
                milestone.title)
