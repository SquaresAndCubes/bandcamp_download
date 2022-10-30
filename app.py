import os
import time
from datetime import datetime
import requests
import json
import mimetypes
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BandcampDownload:

    def __init__(self):
        self.chrome_browser_handle = None
        self.bc_url = 'https://bandcamp.com/'
        self.username = None
        self.log_dir = os.path.join(os.getcwd(), "logs")
        self.logging = False

    def _init_chrome_browser_handle(self):
        webdriver_options = Options()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument('--user-data-dir=C:\\Users\\btvaa\\AppData\\Local\\Google\\Chrome\\User Data')
        webdriver_options.add_argument('--profile-directory=Default')
        webdriver_options.add_argument('--log-level=3')
        return webdriver.Chrome(options=webdriver_options, service=Service(ChromeDriverManager().install()))

    def _get_chrome_browser_handle(self):
        if not self.chrome_browser_handle:
            self.chrome_browser_handle = self._init_chrome_browser_handle()
        if self.chrome_browser_handle:
            return self.chrome_browser_handle
        print(f'!! Failed to get Chrome browser handle !!')
        return False

    def _write_to_file(self, **kwargs):
        filename = kwargs.get('filename', f'{self.log_dir}\log.txt')
        content = kwargs.get('content', None)
        if content:
            with open(filename, 'w', encoding="utf-8") as file:
                if file.write(content):
                    print(f'Wrote to file: {filename}')
                    file.close()
                    return True
                print(f'!! Problem writing file {filename} !!')
                return False
        print('!! Content not provided for writing file !!')
        return False

    def _get_bc_user_collection_url(self):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        _chrome_browser_handle.get(self.bc_url)
        user_collection = _chrome_browser_handle.find_element(By.CSS_SELECTOR, "li#collection-main a")
        return user_collection.get_attribute('href')

    def _expose_all_shows(self, collection_url):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        _chrome_browser_handle.get(collection_url)
        _chrome_browser_handle.find_element(By.CSS_SELECTOR, 'button.show-more').click()
        actions_driver = ActionChains(_chrome_browser_handle)
        for i in range(0,2):
            time.sleep(2)
            actions_driver.key_down(Keys.CONTROL).send_keys(Keys.END).perform()
        html_dump = _chrome_browser_handle.page_source
        timestamp = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
        if self.logging: self._write_to_file(content=html_dump, filename=f'{self.log_dir}\expose_shows_{timestamp}.html')
        return True

    def _get_all_shows_dl_links(self):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        all_show_elements = _chrome_browser_handle.find_elements(By.CSS_SELECTOR, 'div#collection-items li')
        print(f'Found {len(all_show_elements)} shows in {self.username}\'s collection for download')
    
    def _get_xpath(self, tree, search_str):
        return tree.xpath(search_str)
    
    def _get_bc_show_dl_link(self, show_link):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        _chrome_browser_handle.get(show_link)
        wait = WebDriverWait(_chrome_browser_handle, timeout=60)
        download_ready = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='item-button' and @href]")))
        download_url = download_ready.get_attribute("href")
        blob = _chrome_browser_handle.find_element(By.ID, "pagedata").get_attribute("data-blob")
        parse_blob = json.loads(blob)
        show_title = parse_blob["digital_items"][0]["title"]
        show_slug = parse_blob["digital_items"][0]["url_hints"]["slug"]
        return (download_url, show_title, show_slug)

    def init_bc_download(self, logging=False):
        self.logging = logging
        ret = True
        if not self._get_chrome_browser_handle():
            return False
        user_collection_url = self._get_bc_user_collection_url()
        if not user_collection_url:
            print(f'!! Failed to retrieve user collection URL - Are you logged in? !!')
            return False
        self.username = user_collection_url.rsplit('/', 1)[-1]
        print(f'Initializing {self.username}\'s collection from URL: {user_collection_url}')
        if not self._expose_all_shows(user_collection_url):
            print(f'!! Failed to expose all shows for download !!')
            return False
        if not self._get_all_shows_dl_links():
            print(f'!! Failed to retrieve DL links for users collection !!')
            return False
        print(f'Bandcamp user {self.username}\'s shows for download have been successfully identified')

    def download_show(self, show_link):
        show = self._get_bc_show_dl_link(show_link=show_link)
        download_url = show[0]
        show_title = show[1]
        show_slug = show[2]
        print(f'Show Title: {show_title}')
        print(f'Show Name SLUG: {show_slug}')
        download_request = requests.get(download_url, allow_redirects=True)
        content_type = download_request.headers['content-type']
        file_extension = mimetypes.guess_extension(content_type)
        if not file_extension:
            file_extension = '.zip'
        file_path = os.path.join("F:\\", f'{show_slug + file_extension}')
        print(f'Download URL: {download_url}')
        if not os.path.isfile(file_path):
            if open(file_path, 'wb').write(download_request.content):
                print(f'Downloaded show to path: {file_path}')
                return True
        print(f'Filepath: {file_path} - Already downloaded - skipping...')
        return False


if __name__ == "__main__":

    bc_dl = BandcampDownload()
    bc_dl.init_bc_download()