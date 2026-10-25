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
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', project.get('last_updated', '')), project['name']
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
            if publication.get('video_id'):
                for ext in ('mp4', 'jpg'):
                    assert (ROOT / 'assets' / 'papers' / f"{publication['video_id']}.{ext}").exists(), (publication['video_id'], ext)
            if group == 'journal':
                assert publication['status'] == 'published'
            elif group in ('preprint', 'accepted'):
                assert publication['status'] == group
    funding = read('research-projects.json')
    assert funding['records'] and all(p.get('status') and p.get('source_url') for p in funding['records'])

    showcase = read('showcase.json')
    ids = [p['id'] for p in showcase['items']]
    assert len(ids) == len(set(ids)), 'showcase.json: duplicate id'
    for item in showcase['items']:
        assert item['title'] and item['tagline'], item['id']
        assert len(item['tagline']) <= 20, (item['id'], 'tagline > 20 chars')
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', item['date']), item['id']
        for key in ('video', 'cover'):
            assert (ROOT / item[key]).exists(), (item['id'], item[key])
        assert not item.get('source_url') or item['source_url'].startswith('https://'), item['id']

    news = read('announcements.json')
    nids = [n['id'] for n in news['items']]
    assert len(nids) == len(set(nids)), 'announcements.json: duplicate id'
    for n in news['items']:
        assert n['title'] and re.fullmatch(r'\d{4}-\d{2}-\d{2}', n['date']), n['id']
        assert not n.get('link') or n['link'].startswith('https://'), n['id']

    for filename in ('index.html', 'projects.html', 'news.html', 'publications.html', 'research.html', 'dashboard.html', 'map.html'):
        text = (ROOT / filename).read_text(encoding='utf-8')
        parser = HTMLParser()
        parser.feed(text)
        assert 'width=device-width' in text, filename
        assert not FORBIDDEN.search(text), filename
        assert not re.search(r'F1\s*=\s*1\.0|R²\s*=\s*0\.997|24期刊', text), filename

    print(f"PASS: {projects['total']} public project records; " + ', '.join(f'{len(pubs[g])} {g}' for g in GROUPS) + f"; {len(funding['records'])} funding records; {sum(1 for g in GROUPS for p in pubs[g] if p.get('video_id'))} paper videos; {len(showcase['items'])} showcase videos; {len(news['items'])} announcements")


if __name__ == '__main__':
    validate()
