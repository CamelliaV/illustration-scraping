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


def skip(candidates):
  skip = []
  with open('history.txt', 'r', encoding='utf8') as f:
    for line in f.readlines():
      skip += [line.strip()]
    print(skip)
  for v in skip:
    candidates.remove(v)


def finish(history, c):
  history.write(c + '\n')


def jumpback(page, url):
  page.goto(url, wait_until="domcontentloaded")


def download_(page):
  page.wait_for_selector('a[href="javascript:void(0)"]')
  with page.expect_download() as download_info:
    page.query_selector('a[href="javascript:void(0)"]').click()
  download = download_info.value
  download.save_as("res_2/" + download.suggested_filename)


def log(content):
  # logger.write('>>>>>> ' + content + '\n')
  print('>>>>>> ' + content + '\n')
  # logger.flush()


def run(playwright: Playwright) -> None:
  context = playwright.chromium.launch_persistent_context(
      user_data_dir='user-data/', accept_downloads=True, headless=False)
  page = context.pages[0]
  page.set_default_timeout(1_000_000)
  index_url = 'https://wiki.biligame.com/wqmt/%E7%9A%AE%E8%82%A4%E5%9B%BE%E9%89%B4'
  page.goto(index_url)

  candidates = page.query_selector_all('td[data-label="装束名称"] a')

  for i in range(len(candidates)):
    selector = f'tr:nth-of-type({i+1}) td[data-label="装束名称"] a'
    page.wait_for_selector(selector)
    c = page.query_selector(selector)
    name = c.get_attribute('title')
    c.click()
    page.wait_for_event('domcontentloaded')
    log(f'accessing {name}')

    page.query_selector('div.floatnone a').click()
    page.wait_for_event('domcontentloaded')

    log(f'downloading {name}')
    download_(page)

    log(f'downloaded {name}')
    jumpback(page, index_url)
    log('jumpback')

  # ---------------------
  context.close()


with sync_playwright() as playwright:
  run(playwright)
