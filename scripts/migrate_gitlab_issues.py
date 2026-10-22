'''
One-off script to port all issues (with labels and comments) from the
internal GitLab project to GitHub.

Usage:
    export GITLAB_TOKEN=...   # read_api scope
    export GITHUB_TOKEN=...   # issues: write on dfki-ric/CoBaIR
    python scripts/migrate_gitlab_issues.py            # dry run
    python scripts/migrate_gitlab_issues.py --apply    # actually create issues

Already migrated issues are detected by a marker in the issue body,
so the script can safely be re-run.
'''

# System imports
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# end file header
__author__ = 'Adrian Lubitz'

GITLAB_URL = 'https://git.hb.dfki.de'
GITLAB_PROJECT = 'kimmi_sf/implementation/CoBaIR'
GITHUB_REPO = 'dfki-ric/CoBaIR'
MARKER = '<!-- migrated-from-gitlab-iid: {} -->'


def request(url, token_header, data=None, method=None):
    """Perform a JSON request and return (decoded body, response headers). Retries on rate limits."""
    body = json.dumps(data).encode() if data is not None else None
    while True:
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header(*token_header)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read() or 'null'), resp.headers
        except urllib.error.HTTPError as err:
            if err.code in (403, 429) and (err.headers.get('Retry-After')
                                           or err.headers.get('X-RateLimit-Remaining') == '0'):
                wait = int(err.headers.get('Retry-After') or 60)
                print(f'  rate limited, waiting {wait}s')
                time.sleep(wait)
                continue
            raise RuntimeError(f'{method or "GET"} {url} -> {err.code}: {err.read().decode()}') from err


def paginate(url, token_header):
    """Yield all items of a paginated GitLab or GitHub list endpoint."""
    page = 1
    while True:
        sep = '&' if '?' in url else '?'
        items, _ = request(f'{url}{sep}per_page=100&page={page}', token_header)
        if not items:
            return
        yield from items
        page += 1


def convert_text(text, iid_map):
    """Make GitLab markdown safe for GitHub: no foreign @mentions, fixed uploads and issue references."""
    if not text:
        return ''
    project_url = f'{GITLAB_URL}/{GITLAB_PROJECT}'
    # uploads are relative to the GitLab project
    text = re.sub(r'\]\((/uploads/[^)]+)\)', lambda m: f']({project_url}{m.group(1)})', text)
    # GitLab usernames do not correspond to GitHub users -> do not ping anyone
    text = re.sub(r'(?<![\w`/])@([\w.\-]+)', r'`@\1`', text)

    def ref(match):
        iid = int(match.group(1))
        return f'#{iid_map[iid]}' if iid in iid_map else f'GitLab #{iid}'
    text = re.sub(r'(?<![\w&/])#(\d+)\b', ref, text)
    # merge request references would point to unrelated GitHub PRs
    text = re.sub(r'(?<![\w&/])!(\d+)\b', r'GitLab MR !\1', text)
    return text


def main():
    """Run the migration."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--apply', action='store_true', help='create issues on GitHub (default is a dry run)')
    parser.add_argument('--state', choices=['all', 'opened'], default='all', help='which GitLab issues to port')
    args = parser.parse_args()

    gitlab_token = os.environ.get('GITLAB_TOKEN')
    github_token = os.environ.get('GITHUB_TOKEN')
    if not gitlab_token or (args.apply and not github_token):
        sys.exit('GITLAB_TOKEN (and GITHUB_TOKEN for --apply) must be set')
    gl_auth = ('PRIVATE-TOKEN', gitlab_token)
    gh_auth = ('Authorization', f'Bearer {github_token}')
    gl_api = f'{GITLAB_URL}/api/v4/projects/{urllib.parse.quote(GITLAB_PROJECT, safe="")}'
    gh_api = f'https://api.github.com/repos/{GITHUB_REPO}'

    issues = sorted(paginate(f'{gl_api}/issues?state={args.state}', gl_auth), key=lambda i: i['iid'])
    print(f'{len(issues)} GitLab issues found')

    # GitLab #iid -> GitHub number for issues that are already migrated
    iid_map = {}
    if github_token:
        for gh_issue in paginate(f'{gh_api}/issues?state=all', gh_auth):
            found = re.search(r'migrated-from-gitlab-iid: (\d+)', gh_issue.get('body') or '')
            if found:
                iid_map[int(found.group(1))] = gh_issue['number']

    if args.apply:
        labels = {l['name']: l for l in paginate(f'{gl_api}/labels', gl_auth)}
        existing = {l['name'] for l in paginate(f'{gh_api}/labels', gh_auth)}
        for name in sorted({n for i in issues for n in i['labels']} - existing):
            info = labels.get(name, {})
            request(f'{gh_api}/labels', gh_auth, method='POST', data={
                'name': name,
                'color': (info.get('color') or '#ededed').lstrip('#'),
                'description': (info.get('description') or '')[:100]})
            print(f'created label {name}')

    for issue in issues:
        iid = issue['iid']
        if iid in iid_map:
            print(f'GitLab #{iid} already migrated as GitHub #{iid_map[iid]}, skipping')
            continue
        notes = [n for n in paginate(f'{gl_api}/issues/{iid}/notes?sort=asc&order_by=created_at', gl_auth)
                 if not n['system']]
        print(f'GitLab #{iid} [{issue["state"]}] {issue["title"]} '
              f'({len(notes)} comments, labels: {", ".join(issue["labels"]) or "-"})')
        if not args.apply:
            continue

        header = (f'> Migrated from GitLab issue #{iid}, '
                  f'opened by {issue["author"]["name"]} on {issue["created_at"][:10]}')
        if issue.get('milestone'):
            header += f', milestone: {issue["milestone"]["title"]}'
        body = f'{header}\n\n{convert_text(issue["description"], iid_map)}\n\n{MARKER.format(iid)}'
        created, _ = request(f'{gh_api}/issues', gh_auth, method='POST', data={
            'title': issue['title'], 'body': body, 'labels': issue['labels']})
        iid_map[iid] = created['number']
        for note in notes:
            time.sleep(1)  # stay below GitHub's secondary rate limit for content creation
            request(f'{gh_api}/issues/{created["number"]}/comments', gh_auth, method='POST', data={
                'body': f'> {note["author"]["name"]} commented on {note["created_at"][:10]}\n\n'
                        f'{convert_text(note["body"], iid_map)}'})
        if issue['state'] == 'closed':
            request(f'{gh_api}/issues/{created["number"]}', gh_auth, method='PATCH',
                    data={'state': 'closed', 'state_reason': 'completed'})
        print(f'  -> GitHub #{created["number"]}')
        time.sleep(1)

    if args.apply:
        with open('gitlab_github_issue_map.json', 'w', encoding='utf-8') as f:
            json.dump(iid_map, f, indent=2, sort_keys=True)
        print('mapping written to gitlab_github_issue_map.json')
    else:
        print('dry run - rerun with --apply to create the issues on GitHub')


if __name__ == '__main__':
    main()
