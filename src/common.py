import os
import sys
import time
import libarchive
import subprocess
import selenium.common
import selenium.webdriver


class Const:

    ROM_TYPE_LIST = ["nes", "mame"]
    WEBSITE_LIST = ["romhustler.org", "romsmania.cc"]


class Util:

    @staticmethod
    def seleniumGotoDownloadManagerAndWaitUntilDownloadComplete(seleniumDriver, progressFunc=None):
        # Returns (download-url, downloaded-filename)

        seleniumDriver.get("chrome://downloads")
        lastPercentage = -1
        while True:
            time.sleep(1)
            try:
                # get downloaded percentage
                downloadPercentage = seleniumDriver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('#progress').value")
                # report progress
                if downloadPercentage != lastPercentage:
                    if progressFunc is not None:
                        progressFunc(downloadPercentage)
                    lastPercentage = downloadPercentage
                # check if downloadPercentage is 100 (otherwise the script will keep waiting)
                if downloadPercentage == 100:
                    # return the file name once the download is completed
                    realUrl = seleniumDriver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').href")
                    downloadedFile = seleniumDriver.execute_script("return document.querySelector('downloads-manager').shadowRoot.querySelector('#downloadsList downloads-item').shadowRoot.querySelector('div#content  #file-link').text")
                    break
            except Exception:
                pass
        return (realUrl, downloadedFile)

    @staticmethod
    def readFile(filename):
        with open(filename) as f:
            return f.read()


class TempChdir:

    def __init__(self, dirname):
        self.olddir = os.getcwd()
        os.chdir(dirname)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.chdir(self.olddir)


def showProgress(message):
    print("Progress: %s" % (message))


def romDownloadProgressCallback(progress):
    showProgress("ROM download progress %d%%" % (progress))


def getRomInfoForWebSite1(romType, romId, isDebug):
    """Returns (rom-name, direct-download-url, local-file)"""

    # load selenium driver
    options = selenium.webdriver.chrome.options.Options()
    if not isDebug:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
    })
    driver = selenium.webdriver.Chrome(options=options)
    showProgress("Selenium driver loaded.")

    # load rom page
    url = "http://romhustler.org/rom/%s/%s" % (romType, romId)
    driver.get(url)
    showProgress("Target page (%s) loaded." % (url))

    # check if we can download this rom
    try:
        atag = driver.find_element_by_xpath("//div[contains(text(), \"download is disabled\")]")
        raise Exception("download is disabled")
    except selenium.common.exceptions.NoSuchElementException:
        pass

    # get rom-name
    romName = driver.find_element_by_xpath("//h1[@itemprop=\"name\"]").text
    showProgress("ROM name (%s) parsed." % (romName))

    # load download page, click to download
    driver.find_element_by_link_text("Click here to download this rom").click()
    while True:
        time.sleep(1)
        try:
            atag = driver.find_element_by_link_text("here")
            break
        except selenium.common.exceptions.NoSuchElementException:
            pass
    atag.click()
    showProgress("ROM download started.")

    realUrl, downloadedFile = Util.seleniumGotoDownloadManagerAndWaitUntilDownloadComplete(driver, romDownloadProgressCallback)
    showProgress("ROM download completed.")

    return (romName, realUrl, downloadedFile)


def getRomInfoForWebSite2(romType, romId):
    assert False
