# Keep an Azure DevOps board in sync with the work

Use this when the user asks to update the board, backlog or work items of a client (or project) with what
was done in the past weeks ("put it on the board", "update DevOps"). The user works from the work items
and the backlog, so they must be right: complete titles, a good description, the correct Feature and Epic.

## Method

1. Collect sources for the period:
   - the journal of the context, only the content lines, no auto-journal;
   - `git log --all --since=<date> --author=<you>` in every repo of the client, after a fresh
     `git fetch`. Merged PRs show what was really delivered.
2. Make a list of finished pieces of work, one story per deliverable result (not per commit). Work on a
   pushed branch that was tested counts as finished. Tests, explorations and your own tools that are not
   meant for the client do not belong on the board.
3. Fetch the whole board (Epics, Features, all PBIs with parent, state, assignee) and compare it with the
   list. If an existing item already covers the work (even with a general title), do not create a new one.
   An own item that is still New but finished is set to Done and gets a description.
4. Pick the existing Feature for each story. If none fits, create a Feature under the right Epic. Name
   doubtful cases in the answer.
5. Create through the REST API (script below), then check through the API: per item the chain up to its
   Feature and Epic.
6. Report: per item the ID as a link, title, Feature and state, plus what was deliberately not created and
   the doubtful cases.

## Rules

- Titles and descriptions in the language of the board, short and businesslike, plain sentences, one `<p>`
  per sentence. Say what was built, the main models or files, and where it lives (PR numbers or branch).
  No dashes, no AI references.
- Assign to the user, with the iteration as the recent items have. Never invent an iteration, area or ID.
- Do not change items of others. Items you just created may be removed when the user asks; permanent
  removal from the recycle bin is theirs.
- Start no pipelines, notebooks or builds. This is only the board.
- A PBI can only be created in its initial state: POST first, then patch the state.
- Process templates differ: look up the states of this project first (for example New, Approved,
  Committed, Done) and never assume Active or Resolved.

## Script

Put it in the scratchpad as `ado.py` and write a small script per round with `create(...)` calls. Set the
organisation, project, your user and the login folder in environment variables. Use an isolated az login
folder per client (`AZURE_CONFIG_DIR`), and the Azure DevOps application id as token resource (see the
Microsoft documentation).

```python
import json, os, subprocess, sys, urllib.request

ORG = os.environ['ADO_ORG']          # https://dev.azure.com/<organisation>
PROJECT = os.environ['ADO_PROJECT']
ME = os.environ['ADO_USER']          # the user principal name to assign to
RESOURCE = os.environ['ADO_RESOURCE']  # Azure DevOps application id, from the Microsoft docs
ENV = dict(os.environ)               # AZURE_CONFIG_DIR is set per client outside this script
PATCH = 'application/json-patch+json'


def token():
    out = subprocess.run(['az', 'account', 'get-access-token', '--resource', RESOURCE,
                          '--query', 'accessToken', '-o', 'tsv'], capture_output=True, text=True, env=ENV)
    if out.returncode:
        sys.exit(out.stderr)
    return out.stdout.strip()


TOKEN = token()


def call(method, url, body=None, content_type='application/json'):
    if not url.startswith('http'):
        url = ORG + url
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={'Authorization': 'Bearer ' + TOKEN, 'Content-Type': content_type})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def wiql(query):
    res = call('POST', f'/{PROJECT}/_apis/wit/wiql?api-version=7.1', {'query': query})
    ids = [w['id'] for w in res.get('workItems', [])]
    items = []
    for i in range(0, len(ids), 200):
        chunk = ','.join(map(str, ids[i:i + 200]))
        items += call('GET', f'/_apis/wit/workitems?ids={chunk}&$expand=relations&api-version=7.1')['value']
    return items


EXISTING = {w['fields']['System.Title'].lower() for w in wiql(
    f"SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = '{PROJECT}'")}


def create(kind, title, sentences, parent, state):
    """kind: 'Feature' or 'Product%20Backlog%20Item'; state after creation, for example 'Done'."""
    if title.lower() in EXISTING:
        print('ALREADY EXISTS', title)
        return None
    ops = [{'op': 'add', 'path': '/fields/System.Title', 'value': title},
           {'op': 'add', 'path': '/fields/System.Description', 'value': ''.join(f'<p>{s}</p>' for s in sentences)},
           {'op': 'add', 'path': '/fields/System.AssignedTo', 'value': ME},
           {'op': 'add', 'path': '/fields/System.IterationPath', 'value': PROJECT},
           {'op': 'add', 'path': '/relations/-', 'value': {'rel': 'System.LinkTypes.Hierarchy-Reverse',
                                                           'url': f'{ORG}/_apis/wit/workitems/{parent}'}}]
    w = call('POST', f'/{PROJECT}/_apis/wit/workitems/${kind}?api-version=7.1', ops, PATCH)
    if state != 'New':
        w = call('PATCH', f'/_apis/wit/workitems/{w["id"]}?api-version=7.1',
                 [{'op': 'add', 'path': '/fields/System.State', 'value': state}], PATCH)
    print(w['id'], w['fields']['System.State'], title, 'under', parent)
    return w['id']
```

Remove a Feature and its items that have no client value:
`call('DELETE', f'/{PROJECT}/_apis/wit/workitems/<id>?api-version=7.1')` (they go to the recycle bin of the
project).

## Check

Fetch the items again through the API and check per item: title, state, assignee, and the chain to Feature
and Epic. Report only what you saw.

## Self-learning step

When the user corrects the board (another Feature, another wording, an item that should not be there), write
the rule into this skill and, for a client specific indexing, into that client's README.
