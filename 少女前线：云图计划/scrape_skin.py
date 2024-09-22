from playwright.sync_api import Playwright, sync_playwright, expect, Page, TimeoutError as PlaywrightTimeoutError
import re
import asyncio
import requests
from playwright.sync_api import expect

expect.set_options(timeout=10_000_000)

# path_to_extension = "./my-extension"
user_data_dir = "./user-data"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


def skip():
  skip = []
  with open('history.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
      skip += [line.strip()]
    print(skip)
  return skip

def finish(history, c):
  history.write(c + '\n')
  history.flush()


def jumpback(page, url):
  page.goto(url, wait_until="domcontentloaded")

logger = open('log', 'a', encoding='utf8')

def log(content):
  logger.write('>>>>>> ' + content + '\n')
  # print('>>>>>> ' + content + '\n')
  logger.flush()


def run(playwright: Playwright) -> None:
  context = playwright.chromium.launch_persistent_context(
      user_data_dir='user-data/', accept_downloads=True, headless=False)
  page = context.pages[0]
  page.set_default_timeout(1_000_000)
  index_url = 'https://wiki.biligame.com/42lab/%E4%BA%BA%E5%BD%A2%E5%9B%BE%E9%89%B4'
  page.goto(index_url)
  
  history = open('history.txt', 'a', encoding='utf8')
  index_selector = 'span[class="sytx"] > a'
  download_selector = 'div[class="role-box cg"] img'
  skip_set = skip()
  page.wait_for_selector(index_selector)
  all_set = page.query_selector_all(index_selector)
  for i in range(len(all_set)):
    page.wait_for_selector(index_selector)
    candidates = page.query_selector_all(index_selector)
    c = candidates[i]
    name = page.query_selector_all(index_selector)[i].get_attribute('title')
    if name in skip_set or name.find('文件') != -1:
      continue
    c.evaluate_handle('c => c.click()')
    log(f'accessing {name}')
    
    page.wait_for_selector(download_selector)
    imgs = page.query_selector_all(download_selector)
    log(f'downloading {name}')
    print(imgs)
    for img in imgs:
      data = requests.get(img.get_attribute('src'), headers=headers).content
      with open(f'res/{img.get_attribute("alt")}', 'wb') as img_file:
        img_file.write(data)
        
    log(f'downloaded {name}')
    jumpback(page, index_url)
    log('jumpback')
    finish(history, name)
  # ---------------------
  history.close()
  logger.close()
  context.close()


with sync_playwright() as playwright:
  run(playwright)
