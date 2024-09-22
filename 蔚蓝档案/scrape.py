from playwright.sync_api import Playwright, sync_playwright, expect, Page, TimeoutError as PlaywrightTimeoutError
import re
import asyncio
import requests
# path_to_extension = "./my-extension"
user_data_dir = "./user-data"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}


def run(playwright: Playwright) -> None:
  context = playwright.chromium.launch_persistent_context(user_data_dir,
                                                          headless=False, proxy={"server": "http://127.0.0.1:7890"})
  page = context.pages[0]
  page.goto("https://bluearchive.wiki/wiki/Characters_image_list")
  # * remove last three (ad icons)
  imgs = page.query_selector_all('a[title][href*="/wiki/"]:has(img)')
  imgs = [*map(lambda x: x.get_attribute('title'), imgs)]

  skip = []
  with open('history.txt', 'r') as f:
    for line in f.readlines():
      skip += [line.strip()]
    print(skip)
  for v in skip:
    imgs.remove(v)

  for title in imgs:
    page.get_by_role("link", name=title, exact=True).click()
    try:
      page.get_by_role("tab", name="Artwork").click()
      page.get_by_label("Artwork").get_by_role("link", name=title).click()
      page.get_by_role("button", name="Download this file").click()
      with page.expect_popup() as page1_info:
        page.get_by_role("link", name=re.compile(
            r"^Download original file.*")).click()
        page1 = page1_info.value
        url = page1.url
        name = url.split('/')[-1].split('?')[0]
        img = requests.get(url, headers=headers).content
        with open('./artwork/' + name, 'wb') as img_file:
          img_file.write(img)
        page1.close()
    except PlaywrightTimeoutError:
      pass
    try:
      page.get_by_role("button", name="Close this tool (Esc)").click()
      page.get_by_role("tab", name="Other").click()
      page.get_by_role("tab", name="Memorial Lobby").click(timeout=800)
      # page.get_by_label("Other").get_by_role("link").click()
      
      [*filter(lambda x: x.get_attribute('href').find('Memorial_Lobby') != -1,
               page.query_selector_all('.mw-file-description'))][0].click()
      page.get_by_role("button", name="Download this file").click()
      with page.expect_popup() as page2_info:
        page.get_by_role("link", name=re.compile(
            r"^Download original file.*")).click()
        page2 = page2_info.value
        url = page2.url
        name = url.split('/')[-1].split('?')[0]
        img = requests.get(url, headers=headers).content
        with open('./memorialLobby/' + name, 'wb') as img_file:
          img_file.write(img)
        page2.close()
        page.get_by_role("button", name="Close this tool (Esc)").click()
    except PlaywrightTimeoutError:
      pass
    page.goto("https://bluearchive.wiki/wiki/Characters_image_list")
    with open('history.txt', 'a') as f:
      f.write(title + '\n')
  # ---------------------
  context.close()


with sync_playwright() as playwright:
  run(playwright)
