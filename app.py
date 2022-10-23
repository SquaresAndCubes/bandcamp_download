import os
import random
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from slugify import slugify

class BandcampDownload:

    def __init__(self, bc_html):
        self.bc_html = bc_html
        self.html_parser = etree.HTMLParser()
        self.shows_tree = etree.parse(self.bc_html, parser=self.html_parser)
        self.dl_links = self._get_all_show_links(tree=self.shows_tree)
        self.chrome_browser_handle = self._init_chrome_browser_handle()
        self.log_dir = os.path.join(os.getcwd(), "logs")

    def _init_chrome_browser_handle(self):
        webdriver_options = Options()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--user-data-dir=C:\\Users\\btvaa\\AppData\\Local\\Google\\Chrome\\User Data')
        webdriver_options.add_argument('profile-directory=Default')
        return webdriver.Chrome(options=webdriver_options, service=Service(ChromeDriverManager().install()))

    def _get_chrome_browser_handle(self):
        if not self.chrome_browser_handle:
            self.chrome_browser_handle = self._init_chrome_browser_handle()
        if self.chrome_browser_handle:
            return self.chrome_browser_handle
        print(f'!! Issue creating browser handle !!')
        return False
    
    def _get_all_show_links(self, tree):
        refs = self._get_xpath(tree=tree, search_str="//a")
        links = [link.get('href', '') for link in refs]
        return [l for l in links if "https://bandcamp.com/download?from=collection" in l]
    
    def _get_xpath(self, tree, search_str):
        return tree.xpath(search_str)
    
    def _get_bc_show_dl_link(self, show_link):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        _chrome_browser_handle.get(show_link)
        wait = WebDriverWait(_chrome_browser_handle, timeout=30)
        download_ready = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='item-button' and @href]")))
        download_url = download_ready.get_attribute("href")
        show_name = _chrome_browser_handle.find_element(By.CLASS_NAME, "title").text
        return (download_url, show_name)

    def download_show(self, show_link):
        download_url, show_name = self._get_bc_show_dl_link(show_link=show_link)
        print(f'Show Name: {show_name}')
        show_name_slug = slugify(show_name)
        print(f'Show Name SLUG: {show_name_slug}')
        print(f'Download URL: {download_url}')
        download_request = requests.get(download_url, allow_redirects=True)
        file_path = os.path.join("D:\MUSIC\FLAC\STS9", f'{show_name_slug}.zip')
        if open(file_path, 'wb').write(download_request.content):
            print(f'Downloaded show to path: {file_path}')


if __name__ == "__main__":

    bc_dl = BandcampDownload(bc_html="bandcamp_dump.html")
    print(f'Found {len(bc_dl.dl_links)} shows for download')
    bc_dl.download_show(show_link=bc_dl.dl_links[random.randint(0, len(bc_dl.dl_links))])
