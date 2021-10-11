from tkinter import filedialog
from tkinter import *
import glob
import os,time
import sys,json
import win32com.client 
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import multiprocessing
from win32com.client import Dispatch 
import requests
import wget
import zipfile


def split(a, n):
    k, m = divmod(len(a), n)
    return list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)))

def read_file():
    try:
        file = open('resultCodes.txt','r')
    except:
        open('resultCodes.txt','w').close()
        return []
    lines = []
    for line in file.readlines():
        if line.strip():
            lines.append(line)
    file.close()

    return lines

def append_in_text_file(code,lock):
    lock.acquire()
    if code in read_file():
        print("** CODE ALREADY IN FILE")
        return
    try:
        file = open('resultCodes.txt','w')
    except:
        file = open('resultCodes.txt','a')
    file.write(str(code)+'\n')
    file.close()
    lock.release()

def clear_win():
    os.system('cls') if os.name == 'nt' else os.system('clear')

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



def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject")     
    version = parser.GetFileVersion(filename)     
    return version 

def install_chromedriver(version_number):
    
    # get the latest chrome driver version number
    url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
    response = requests.get(url)
    version_number = response.text

    # build the donwload url
    download_url = "https://chromedriver.storage.googleapis.com/" + version_number +"/chromedriver_win32.zip"

    # download the zip file using the url built above
    latest_driver_zip = wget.download(download_url,'chromedriver.zip')

    # extract the zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
        zip_ref.extractall() # you can specify the destination folder path here
    # delete the zip file downloaded above
    os.remove(latest_driver_zip)


def get_driver(profilePath,profileName):
    

    print([profilePath,profileName])
    options = webdriver.ChromeOptions()
    options.add_experimental_option('w3c', False) ### added this line
    completePath = os.path.join(profilePath,profileName)
    options.add_argument("user-data-dir={}".format(completePath) )
    options.add_argument("--log-level=0")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # options.add_argument("profile-directory={}".format(profileName))

    cap = DesiredCapabilities.CHROME
    cap['loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(desired_capabilities = cap, options=options)
    return driver

def oneChunkHandler(chunk,folder,profilesFolderPath,lock):
    for file in chunk:
        profileName = get_taget_profile(os.path.join(folder,file))
        print("** FETCHING CODE FOR PROFILE -> ", profileName)
        driver = get_driver(profilesFolderPath,profileName)
        driver.get('https://discord.com/channels/@me')
        time.sleep(5)
        try:
            driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("//button[@aria-label='User settings' or @aria-label='User Settings']"))
            # time.sleep(5)
            # driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("//div[@aria-controls='advanced-tab']"))
            # time.sleep(2)
            # driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("(//input[@type='checkbox'])[1]"))
            # time.sleep(2)
            # driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("(//input[@type='checkbox'])[1]"))
            time.sleep(2)
            logs = driver.get_log('performance')
            code = None
            for l in logs:
                try:
                    code = str(l).split('"authorization"')[1].split('",')[0].replace('"','').replace(':','').strip()
                    break
                except:
                    pass
            
            print("** CODE -> ", [code])
            if code:
                append_in_text_file(code,lock)

        except Exception as e:
            print(e)    
            print("** ERROR WHILE THIS PROFILE....")
            time.sleep(2)

        try:driver.quit()
        except:pass

def main():
    folder = get_folder_path()
    app_data = os.getenv('APPDATA')
    app_data = os.path.abspath(os.path.join(app_data, '..'))
    profilesFolderPath =  os.path.join(app_data,'Local','Google','Chrome','User Data')  
    files = list(os.walk(folder))[0][2]
    chunks = split(files,5)
    processes = [None] * len(chunks)
    lock = multiprocessing.Lock()
    for p in range(len(processes)):
        processes[p] = multiprocessing.Process(target=oneChunkHandler,args=(chunks[p],folder,profilesFolderPath,lock,))
        processes[p].start()
    
    for p in processes:
        p.join()

    
if __name__ == "__main__":
    multiprocessing.freeze_support()

    print("\n BOT STARTING......")
    if not os.path.exists(os.path.join(os.getcwd(),'chromedriver.exe')):
        path = os.path.join(os.environ["ProgramFiles"],'Google','Chrome','Application','chrome.exe') if os.path.exists(os.path.join(os.environ["ProgramFiles"],'Google','Chrome','Application','chrome.exe')) else os.path.join(os.environ["ProgramFiles(x86)"],'Google','Chrome','Application','chrome.exe')
        version = get_version_via_com(path)
        install_chromedriver(version)
    main()
    print("\n BOT JOB DONE \n")
    while 1:pass