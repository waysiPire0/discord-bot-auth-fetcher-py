from tkinter import filedialog
from tkinter import *
import glob
import os,time
import sys,json
import win32com.client 
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By



def read_file():
    file = open('resultCodes.txt','r')
    lines = []
    for line in file.readlines():
        if line.strip():
            lines.append(line)
    file.close()
    return lines

def append_in_text_file(code):
    if code in read_file():
        print("** CODE ALREADY IN FILE")
        return
    try:
        file = open('resultCodes.txt','w')
    except:
        file = open('resultCodes.txt','a')
    file.write(str(code)+'\n')
    file.close()

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

def main():
    folder = get_folder_path()
    app_data = os.getenv('APPDATA')
    app_data = os.path.abspath(os.path.join(app_data, '..'))
    profilesFolderPath =  os.path.join(app_data,'Local','Google','Chrome','User Data')  
    files = list(os.walk(folder))[0][2]
    for file in files:
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
                append_in_text_file(code)

        except Exception as e:
            print(e)    
            print("** ERROR WHILE THIS PROFILE....")
            time.sleep(2)

        try:driver.quit()
        except:pass

if __name__ == "__main__":
    print("\n BOT STARTING......")
    main()
    print("\n BOT JOB DONE \n")
    while 1:pass