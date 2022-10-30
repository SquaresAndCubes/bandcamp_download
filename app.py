import os
import time
from datetime import datetime
import requests
import json
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

    def __init__(self, **kwargs):
        self.chrome_user_data_dir = None
        self.chrome_user_profile_dir = None
        self.bc_url = 'https://bandcamp.com/'
        self.bc_dl_init = False
        self.chrome_browser_handle = None
        self.bc_username = None
        self.log_dir = os.path.join(os.getcwd(), "logs")
        self.show_download_elements = []
        self.show_download_urls = []
        self.all_shows_final_download_info = []
        self.download_path = 'C:\\STS9'
        self.logging = False

    def _init_chrome_browser_handle(self):
        webdriver_logging = 3
        webdriver_options = Options()
        webdriver_options.add_argument('--headless')
        webdriver_options.add_argument(f'--user-data-dir={self.chrome_user_data_dir}')
        webdriver_options.add_argument(f'--profile-directory={self.chrome_user_profile_dir}')
        if self.logging: webdriver_logging = 0
        webdriver_options.add_argument(f'--log-level={webdriver_logging}')
        return webdriver.Chrome(options=webdriver_options, service=Service(ChromeDriverManager().install()))

    def _get_chrome_browser_handle(self):
        if not self.chrome_browser_handle: 
            self.chrome_browser_handle = self._init_chrome_browser_handle()
        if self.chrome_browser_handle: return self.chrome_browser_handle
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
        print(f'\nExposing all shows in user {self.bc_username}\'s collection. Please wait...')
        for i in range(0, 50):
            time.sleep(2)
            actions_driver.key_down(Keys.CONTROL).send_keys(Keys.END).perform()
        html_dump = _chrome_browser_handle.page_source
        timestamp = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
        if self.logging: self._write_to_file(content=html_dump, filename=f'{self.log_dir}\expose_shows_{timestamp}.html')
        return True

    def _generate_download_urls(self):
        self.show_download_elements = self.chrome_browser_handle.find_elements(By.XPATH, '//span[@class="redownload-item"]/a')
        print(f'---> Found {len(self.show_download_elements)} shows in {self.bc_username}\'s collection for download')
        if self.quantity:
            print(f'!! User has provided a show quantity. Limiting scope to {self.quantity} shows !!\n')
            self.show_download_elements = self.show_download_elements[0:self.quantity]
        for show in self.show_download_elements:
            show_url = show.get_attribute('href')
            self.show_download_urls.append(show_url)
        return True
    
    def _get_show_download_file_url(self, show_download_url):
        _chrome_browser_handle = self._get_chrome_browser_handle()
        _chrome_browser_handle.get(show_download_url)
        wait = WebDriverWait(_chrome_browser_handle, timeout=60)
        download_ready = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='item-button' and @href]")))
        download_url = download_ready.get_attribute("href")
        if not download_url:
            print(f'Failed to retrieve file download URL for show at URL: {show_download_url}')
            return False
        blob = _chrome_browser_handle.find_element(By.ID, "pagedata").get_attribute("data-blob")
        parse_blob = json.loads(blob)
        show_title = parse_blob["digital_items"][0]["title"]
        show_slug = parse_blob["digital_items"][0]["url_hints"]["slug"]
        return {'show_title': show_title, 'show_slug': show_slug, 'download_url': download_url}

    def _get_all_shows_final_download_info(self):
        for show_download_url in self.show_download_urls:
            show = self._get_show_download_file_url(show_download_url)
            print(f'############################################################')
            print(f'TITLE: {show["show_title"]}')
            print(f'SLUG: {show["show_slug"]}')
            print(f'DL URL: {show["download_url"]}')
            self.all_shows_final_download_info.append(show)
        print('############################################################')
        print('All shows final download info process completed. Ready to download_shows()')
        return True

    def _download_show(self, show):
        print('############################################################')
        print(f'Downloading ---> {show["show_title"]} \nFrom URL: {show["download_url"]}')
        file_path = os.path.join(self.download_path, f'{show["show_slug"]}.zip')
        if os.path.isfile(file_path):
            print(f'!! Filepath: {file_path} is already downloaded --> Skipping !!')
            return False
        download_request = requests.get(show['download_url'], allow_redirects=True)
        if not download_request:
            print('!! Could not download show !!')
        if open(file_path, 'wb').write(download_request.content):
            print(f'Downloaded show to path: {file_path}')
            return True
        return False

    #Must run this first passing in desired target download directory and Chrome user data directory if necessary
    def init_bc_download(self, **kwargs):
        print('\n')
        print('!! Welcome to Bandcamp Download !!')
        print('\n')
        print('Initializing. Please wait...')
        self.chrome_user_data_dir = kwargs.get('chrome_user_data_dir', f'{os.environ["USERPROFILE"]}\\AppData\\Local\\Google\\Chrome\\User Data')
        self.chrome_user_profile_dir = kwargs.get('chrome_user_profile_dir', 'Default')
        self.download_path = kwargs.get('download_path', 'C:\\STS9')
        if not os.path.isdir(self.download_path):
            os.mkdir(self.download_path)
            print(f'Show download path {self.download_path} created')
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
            print(f'Log directory {self.log_dir} created ')
        self.quantity = kwargs.get('quantity', False)
        self.logging = kwargs.get('logging', False)
        if not self._get_chrome_browser_handle(): return False
        user_collection_url = self._get_bc_user_collection_url()
        if not user_collection_url:
            print(f'!! Failed to retrieve user collection URL - Are you logged in? !!')
            return False
        self.bc_username = user_collection_url.rsplit('/', 1)[-1]
        print(f'\nInitializing {self.bc_username}\'s collection from ---> URL: {user_collection_url}')
        if not self._expose_all_shows(user_collection_url):
            print(f'!! Failed to expose all shows for download !!')
            return False
        print(f'\nGathering show download URLs...')
        if not self._generate_download_urls():
            print(f'!! Failed to identify shows from {self.bc_username}\'s collection !!')
        print('\nBandcamp Download initialization completed !!\n')
        self.bc_dl_init = True
        return True
    
    def download_shows(self):
        if not self.bc_dl_init:
            print('!! Bandcamp Download has not been initialized !!')
            print("Please run BandcampDownload().init_bc_download(logging=False, download_path='D:\\MUSIC\\FLAC\\STS9') first !!, quantity=False")
        for show_download_url in self.show_download_urls:
            show = self._get_show_download_file_url(show_download_url)
            if show: self._download_show(show)
            continue


if __name__ == "__main__":

    bc_dl = BandcampDownload()
    bc_dl.init_bc_download(logging=False, download_path='D:\\STS9', quantity=10)
    bc_dl.download_shows()