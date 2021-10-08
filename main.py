from tkinter import filedialog
from tkinter import *
import glob
import os,time
import sys
import win32com.client 
from selenium import webdriver


def get_folder_path():
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    return folder_selected

def get_taget_profile(filePath):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(filePath)
    args = shortcut.Arguments
    targetProfile = args.split('=')[-1].replace('"','')
    return targetProfile

def get_driver(profilePath,profileName):
    print([profilePath,profileName])
    options = webdriver.ChromeOptions()
    completePath = os.path.join(profilePath,profileName)
    options.add_argument("user-data-dir={}".format(profilePath) )
    options.add_argument("profile-directory={}".format(profileName))
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    return driver

def main():
    folder = get_folder_path()
    app_data = os.getenv('APPDATA')
    app_data = os.path.abspath(os.path.join(app_data, '..'))
    profilesFolderPath =  os.path.join(app_data,'Local','Google','Chrome','User Data')  
    files = list(os.walk(folder))[0][2]
    for file in files:
        profileName = get_taget_profile(os.path.join(folder,file))
        driver = get_driver(profilesFolderPath,profileName)
        driver.get('https://discord.com/channels/@me')
        time.sleep(2)
        driver.find_element_by_xpath("//button[@aria-label='User settings']").click()
        time.sleep(2)
        driver.find_element_by_xpath('//div[@aria-controls="advanced-tab"]').click()
        time.sleep(2)
        driver.find_element_by_xpath('(//input[@type="checkbox"])[1]').click()
        time.sleep(4)
        driver.find_element_by_xpath('(//input[@type="checkbox"])[1]').click()
        time.sleep(4)
        test = driver.execute_script("var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;")
        for item in test:
            print(item)

        while 1:pass


if __name__ == "__main__":
    main()

    # C:\Users\hp\AppData\Local\Google\Chrome