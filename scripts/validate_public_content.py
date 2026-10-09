"""Validate the public website catalogue without external dependencies."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_FIELDS = {
    'name', 'name_zh', 'category', 'technologies', 'last_updated',
    'description_zh', 'status', 'source_note', 'source_url',
    'repository_url', 'outputs',
}
FORBIDDEN = re.compile(r'(/sessions/|/workspace/|[A-Z]:\\\\|_yaml_path|local_folder|next_milestone|this_session|product_owner)')
GROUPS = ('journal', 'conference', 'preprint', 'accepted', 'patent', 'award')


def read(name):
    text = (ROOT / name).read_text(encoding='utf-8')
    assert not FORBIDDEN.search(text), f'{name}: private operational content'
    return json.loads(text)


def validate():
    projects = read('data.json')
    assert projects['total'] == len(projects['projects'])
    assert len({p['name'] for p in projects['projects']}) == projects['total']
    for project in projects['projects']:
        assert set(project) <= PROJECT_FIELDS, (project['name'], set(project) - PROJECT_FIELDS)
        assert 'progress' not in project and 'key_metrics' not in project
        assert project['name'] and project['description_zh']
        for key in ('source_url', 'repository_url'):
            if project.get(key):
                assert project[key].startswith('https://'), (project['name'], key)

    pubs = read('publications.json')
    for group in GROUPS:
        items = pubs[group]
        keys = [(p['year'], p['title']) for p in items]
        assert len(keys) == len(set(keys)), f'{group}: duplicate record'
        for publication in items:
            assert publication['title'] and publication.get('source_url')
            assert not re.search(r'under review|submitted|draft', publication.get('status', ''), re.I)
            if group == 'journal':
                assert publication['status'] == 'published'
            elif group in ('preprint', 'accepted'):
                assert publication['status'] == group
    funding = read('research-projects.json')
    assert funding['records'] and all(p.get('status') and p.get('source_url') for p in funding['records'])

    for filename in ('index.html', 'projects.html', 'publications.html', 'research.html', 'dashboard.html', 'map.html'):
        text = (ROOT / filename).read_text(encoding='utf-8')
        parser = HTMLParser()
        parser.feed(text)
        assert 'width=device-width' in text, filename
        assert not FORBIDDEN.search(text), filename
        assert not re.search(r'F1\s*=\s*1\.0|R²\s*=\s*0\.997|24期刊', text), filename

    print(f"PASS: {projects['total']} public project records; " + ', '.join(f'{len(pubs[g])} {g}' for g in GROUPS) + f"; {len(funding['records'])} funding records")


if __name__ == '__main__':
    validate()
