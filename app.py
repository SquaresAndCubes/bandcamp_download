from lxml import etree, html
from io import StringIO
import requests

class BandcampDownload:

    def __init__(self, bc_html):
        self.bc_html = bc_html
        self.dl_link_url_str = "https://bandcamp.com/download?from=collection"
        self.parser = etree.HTMLParser()
        self.tree = etree.parse(self.bc_html, parser=self.parser)
        self.dl_links = self._get_all_show_links(self.tree)

    def _get_all_show_links(self, tree):
        refs = tree.xpath("//a")
        links = [link.get('href', '') for link in refs]
        return [l for l in links if self.dl_link_url_str in l]

    def _get_bc_show_dl_link(self, link):
        show = requests.get(link)
        show_html = show.content.decode("utf-8")
        show_tree = etree.parse(StringIO(show_html), parser=self.parser)
        dl_ref = show_tree.xpath('.//a[text()="Download"]')[0]
        return dl_ref.get('href', '')

    def download_show(self, link):
        show = self._get_bc_show_dl_link(link)
        


if __name__ == "__main__":

    bc_dl = BandcampDownload(bc_html="bandcamp_dump.html")
    first_show_link = bc_dl.dl_links[0]
    print(f'Found {len(bc_dl.dl_links)} shows for download')
    print(f'First Show: {first_show_link}')
    bc_dl._get_bc_show_dl_link(first_show_link)