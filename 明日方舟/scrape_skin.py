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


def download_(page):
  page.wait_for_selector('a[href="javascript:void(0)"]')
  with page.expect_download() as download_info:
    page.query_selector('a[href="javascript:void(0)"]').click()
  download = download_info.value
  download.save_as("res_2/" + download.suggested_filename)

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
  index_url = 'https://wiki.biligame.com/arknights/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
  page.goto(index_url)
  history = open('history.txt', 'a', encoding='utf8')
  skip_set = skip()
  selector = 'div[class="operator-handbook-item-wrapper"] > p > a'
  all_set = page.query_selector_all(selector)
  len_tabs = len(page.query_selector_all('div.resp-tab-content'))
  cnts = [0] * len_tabs
  for i in range(1, len_tabs + 1):
    cnts[i - 1] = len(page.query_selector_all(f'div.resp-tab-content:nth-of-type({i}) div.operator-handbook-item-wrapper'))
  for i in range(1, len_tabs):
    cnts[i] += cnts[i - 1]
  j = 0
  for i in range(len(all_set)):
    page.wait_for_selector(selector)
    candidates = page.query_selector_all(selector)
    c = candidates[i]
    name = page.query_selector_all('div[class="operator-handbook-item-wrapper"] div.operator-handbook-item-name')[i].inner_text()
    if name in skip_set:
      continue
    while i >= cnts[j]:
      j += 1
    page.query_selector_all('span[class="tab-panel"]')[j].click()
    print(c)
    
    c.click()
    page.wait_for_event('domcontentloaded')
    log(f'accessing {name}')
    
    imgs = page.query_selector_all('div#illustrations div[class="switch-tab-contents"] div.switch-tab-content img')
    log(f'downloading {name}')
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
