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
  index_url = 'https://www.gfwiki.org/w/%E9%A6%96%E9%A1%B5'
  page.goto(index_url)
  page.query_selector_all('a[title="装扮一览"]')[0].click()
  page.wait_for_event('domcontentloaded')
  
  history = open('history.txt', 'a', encoding='utf8')
  page_selector = 'table.pageControl:first-of-type div.pageNumber'
  page_locator =  page.locator(page_selector)
  item_selector = 'div.onesuit a'
  item_locator =  page.locator(item_selector)
  name_selector =  page.locator('div.onesuit a')
  
  img_selector = page.locator('div.picndiv')
  skin_name_selector = page.locator('div.picndiv div.skinname')
  
  skip_set = skip()
  print('ready')
  
  
  page.wait_for_selector(page_selector)
  pages = page.query_selector_all(page_selector)
  for i in range(len(pages)):
    print('start')
    page.wait_for_selector(page_selector)
    page.query_selector_all(page_selector)[i].click()
    import time
    time.sleep(1)
    # * got to wait
    page.wait_for_selector(item_selector)
    items = page.query_selector_all(item_selector)
    print(items)
    for j in range(len(items)):
      print(j)
      time.sleep(1)
      page.wait_for_selector(item_selector)
      name = page.query_selector_all(item_selector)[j].text_content()
      if name in skip_set:
        continue
      log(f'accessing {name}')
      page.wait_for_selector(item_selector)
      page.query_selector_all(item_selector)[j].click()
      
      page.wait_for_selector('div.picndiv')
      imgs = page.query_selector_all('div.picndiv')
      log(f'downloading {name}')
      
      # import time
      # time.sleep(1)
      for k in range(len(imgs)):
        import time
        time.sleep(1)
        imgs = page.query_selector_all('div.picndiv')
        imgs[k].click()
        time.sleep(1)
        skin = page.query_selector('img#thepic')
        src = skin.get_attribute('src')
        if src == None or src == '':
          continue
        skin_name = page.query_selector_all('div.picndiv div.skinname')[k].text_content()
        skin_name = skin_name.replace('/', ' ').replace("'", ' ').replace('"', ' ').replace('?', ' ')
        data = requests.get(src, headers=headers).content
        with open(f'res/{skin_name}1.png', 'wb') as img_file:
          img_file.write(data)
        # * read only offsetX cannot launch mouse event

        skin.click(position={'x': 360, 'y': 360})
        time.sleep(1)
        skin = page.query_selector('img#thepic')
        data = requests.get(skin.get_attribute('src'), headers=headers).content
        with open(f'res/{skin_name}2.png', 'wb') as img_file:
          img_file.write(data)
        # * need to resolve or end up with old element click wrong position
        skin.click(position={'x': 360, 'y': 360})
        

      log(f'downloaded {name}')
      page.go_back()
      page.wait_for_selector(page_selector)
      page.query_selector_all(page_selector)[i].click()
      log('jumpback')
      finish(history, name)
  # ---------------------
  history.close()
  logger.close()
  context.close()


with sync_playwright() as playwright:
  run(playwright)
