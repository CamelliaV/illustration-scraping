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
  # page.get_by_role("button", name="查看全部").click()
  # page.get_by_role("button", name="女").click()


logger = open('log', 'a', encoding='utf8')


def download_(page):
  page.wait_for_selector('a[href="javascript:void(0)"]')
  with page.expect_download() as download_info:
    page.query_selector('a[href="javascript:void(0)"]').click()
  download = download_info.value
  download.save_as("res/" + download.suggested_filename)


def log(content):
  logger.write('>>>>>> ' + content + '\n')
  logger.flush()


def run(playwright: Playwright) -> None:
  context = playwright.chromium.launch_persistent_context(
      user_data_dir='user-data/', accept_downloads=True, headless=False)
  page = context.pages[0]
  page.set_default_timeout(1_000_000)
  page.goto("https://wiki.biligame.com/wqmt/%E7%A6%81%E9%97%AD%E8%80%85")
  # page.get_by_role("button", name="查看全部").click()
  # page.get_by_role("button", name="女").click()
  candidates = page.query_selector_all(
      'tr.mtr[data-param5="女"] > td:first-child > a')
  candidates = [*map(lambda x: x.get_attribute('title'), candidates)]
  history = open('history.txt', 'a', encoding='utf8')
  skip(candidates)

  for c in candidates:
    page.get_by_text(c, exact=True).click()
    page.wait_for_event('domcontentloaded')
    log(f'accessing {c}')
    # print(tabs)
    url = page.url
    # * try catch
    for i in range(4):
      try:
        tabs = page.query_selector_all('span.tab-panel')
        tabs = [*filter(lambda x: x.text_content()
                        in ['立绘', '升阶', '证件照', '审讯'], tabs)]
        tabs = tabs[-4:]
        print(tabs)
        while tabs[0].inner_text() != '立绘':
          tabs.pop(0)
        if i == len(tabs):
          log(f'--------- {c} total: {i}')
          break
        tab = tabs[i]
        # * tab elementhandle for position, got to save content, new page won't find it
        name = tab.inner_text()
        log(f'subitem {name}')
        tab.click()
        try:
          page.query_selector_all(
            f'a[title="文件:{c}{tab.inner_text()}.png"]')[1].click()
        except:
          log(f'skip invalid subitem {name}')
          continue
        page.wait_for_event('domcontentloaded')

        log(f'downloading {name}')
        download_(page)
        log(f'downloaded {name}')
        jumpback(page, url)
        log('jumpback')
      except PlaywrightTimeoutError:
        pass
    # * download
    jumpback(page, "https://wiki.biligame.com/wqmt/%E7%A6%81%E9%97%AD%E8%80%85")
    finish(history, c)

  # ---------------------
  history.close()
  logger.close()
  context.close()


with sync_playwright() as playwright:
  run(playwright)

  #     name = url.split('/')[-1].split('?')[0]
  #     img = requests.get(url, headers=headers).content
  #     with open('./artwork/' + name, 'wb') as img_file:
  #       img_file.write(img)
  #     page1.close()
  # except PlaywrightTimeoutError:
  #   pass
  # try:
  #   page.get_by_role("button", name="Close this tool (Esc)").click()
  #   page.get_by_role("tab", name="Other").click()
  #   page.get_by_role("tab", name="Memorial Lobby").click(timeout=800)
  #   # page.get_by_label("Other").get_by_role("link").click()

  #   [*filter(lambda x: x.get_attribute('href').find('Memorial_Lobby') != -1,
  #            page.query_selector_all('.mw-file-description'))][0].click()
  #   page.get_by_role("button", name="Download this file").click()
  #   with page.expect_popup() as page2_info:
  #     page.get_by_role("link", name=re.compile(
  #         r"^Download original file.*")).click()
  #     page2 = page2_info.value
  #     url = page2.url
  #     name = url.split('/')[-1].split('?')[0]
  #     img = requests.get(url, headers=headers).content
  #     with open('./memorialLobby/' + name, 'wb') as img_file:
  #       img_file.write(img)
