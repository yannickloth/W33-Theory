"""Monitor arXiv for new papers on Vogel universality and related topics.

This simple script queries the arXiv API for the given search terms and
prints out title, authors, and abstract for the most recent entries.  It
can be run periodically or integrated into a larger workflow.
"""
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BASE = "http://export.arxiv.org/api/query?"


def search_arxiv(query, max_results=5):
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'lastUpdatedDate',
        'sortOrder': 'descending'
    }
    url = BASE + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = resp.read().decode('utf-8')
    return data


def parse_and_print(xml_data):
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns)]
        link = entry.find("atom:link[@type='text/html']", ns).attrib['href']
        print(f"Title: {title}")
        print(f"Authors: {', '.join(authors)}")
        print(f"Link: {link}")
        print(f"Abstract: {summary[:400]}...")
        print('-' * 80)


def main():
    queries = [
        'all:Vogel+universal',
        'all:universal+Lie+algebra',
        'all:Macdonald+dimensions',
        'all:Jacobi+identity+Vogel'
    ]
    for q in queries:
        print(f"\n=== arXiv search for '{q}' ===")
        data = search_arxiv(q, max_results=3)
        parse_and_print(data)


if __name__ == '__main__':
    main()
