from lxml import etree, html
from io import StringIO
import requests
import time

class BandcampDownload:

    def __init__(self, bc_html):
        self.bc_html = bc_html
        self.dl_link_url_str = "https://bandcamp.com/download?from=collection"
        self.parser = etree.HTMLParser()
        self.tree = etree.parse(self.bc_html, parser=self.parser)
        self.dl_links = self._get_all_show_links(tree=self.tree)

    def _get_all_show_links(self, tree):
        refs = self._get_xpath(tree=tree, search_str="//a")
        links = [link.get('href', '') for link in refs]
        return [l for l in links if self.dl_link_url_str in l]

    def _get_show_tree(self, link):
        show = requests.get(link)
        print(f'Show HTML encoding: {show.encoding}')
        show_text = show.text
        show_tree = etree.parse(StringIO(show_text), parser=self.parser)
        return (show_tree, show_text)
    
    def _get_xpath(self, tree, search_str):
        return tree.xpath(search_str)
    
    def _get_bc_show_dl_link(self, show_link, search_str):
        show_tree = self._get_show_tree(link=show_link)[0]
        dl_ref = self._get_xpath(tree=show_tree, search_str=search_str)
        print(f'dl_ref: {dl_ref}')
        return True

    def save_to_file(self, data, filename):
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(data)
        file.close()
        print(f'Wrote to file: {filename}')

    def download_show(self, show_link):
        show = self._get_bc_show_dl_link(show_link=show_link)
        
if __name__ == "__main__":

    bc_dl = BandcampDownload(bc_html="bandcamp_dump.html")
    first_show_link = bc_dl.dl_links[10]
    print(f'Found {len(bc_dl.dl_links)} shows for download')
    print(f'First Show: {first_show_link}')
    tree = bc_dl._get_show_tree(first_show_link)
    #print(tree[2].content)
    #print(bc_dl._get_xpath(tree=tree[0], search_str="//a"))
    bc_dl.save_to_file(data=tree[1], filename='first_show_text.txt')
    #first_show_dl_link = bc_dl._get_bc_show_dl_link(first_show_link)
    #print(first_show_dl_link)