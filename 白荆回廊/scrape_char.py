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
  index_url = 'https://wiki.biligame.com/bjhl/%E5%90%8C%E8%B0%83%E8%80%85%E5%9B%BE%E9%89%B4'
  page.goto(index_url)

  history = open('history.txt', 'a', encoding='utf8')
  index_selector = 'div.divsort[data-param4="女"] > div:first-of-type > a'
  download_selector = 'div[data-img*="S4"] img'
  skip_set = skip()
  all_set = page.query_selector_all(index_selector)
  for i in range(len(all_set)):
    page.wait_for_selector(index_selector)
    candidates = page.query_selector_all(index_selector)
    c = candidates[i]
    name = c.get_attribute('title')
    if name in skip_set:
      continue
    c.click()
    page.wait_for_event('domcontentloaded')
    log(f'accessing {name}')

    img = page.query_selector_all(download_selector)
    if len(img) == 0:
      page.goto(index_url)
      log('skip')
      finish(history, name)
      continue
    img = img[0]
    log(f'downloading {name}')
    
    data = requests.get(img.get_attribute('src'), headers=headers).content
    with open(f'res/{img.get_attribute("alt")}', 'wb') as img_file:
      img_file.write(data)

    log(f'downloaded {name}')
    page.goto(index_url)
    log('jumpback')
    finish(history, name)
  # ---------------------
  history.close()
  logger.close()
  context.close()


with sync_playwright() as playwright:
  run(playwright)
