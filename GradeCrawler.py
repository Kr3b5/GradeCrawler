#!/usr/bin/env python
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from datetime import datetime
from socket import gaierror
from time import sleep
import smtplib
import getpass

#-------------------------------------------------------------------------------
#                                   INFO
#-------------------------------------------------------------------------------
# Simple Grade Crawler for DHGE SelfService
# Version: 1.0
#
#   Setup:
#       1. Extract script and Firefoxdriver (geckodriver) in the same diretory
#               Firefox-Driver: https://github.com/mozilla/geckodriver/releases
#       2. Install selenium with "pip install selenium"
#   How to use:
#       1. Configurate the script at section CONFIG or use the init wizard
#          (activate use_wizard in section WIZARDs)
#       2. Start the script with py GradeCrawler.py
#       -> To exit close terminal/cmd or press strg+c
#
#   -> Script create data at first run, check grades in terminal! Later the
#      script sends notification mails if new grades detected
#
# Attention! This crawler use Firefox as Seleniumdriver, but Chrome can be
# used too.
#   Chromedriver download:
#       https://chromedriver.chromium.org/downloads
#   Config:
#       Search for line "driver = webdriver.Firefox()" and edit it to
#       "driver = webdriver.Chrome()"
#
# Copyright by Kr3b5


#-------------------------------------------------------------------------------
#                                   WIZARD
#-------------------------------------------------------------------------------
use_wizard = False           #(True/False)

#-------------------------------------------------------------------------------
#                                   CONFIG
#-------------------------------------------------------------------------------
# Credentials DHGE-Service
url_dhge = "https://gera.dhge.de/SelfService/start.php"
matnr = ""
passw = "!"
semester = 3

#Features
want_Mail = True #(True/False) want a Mail -> config SMTP Server

#Filename
file_name = "grades_" + str(semester) + ".txt"

#Delay Check / Online Time
delay = 1800    #1min = 60
start_time = 7
end_time = 18

#SMTP Server (Mail)
port = 1025
smtp_server = "localhost"
login = ""
password = ""

# Mail Content
sender = "GradeService@test.com"
receiver = "Me@test.com"
subject = "Neue Noten"
#-------------------------------------------------------------------------------
#                   DEV-CONFIG - activate only for Dev
#-------------------------------------------------------------------------------

#url_dhge = "http://localhost/noten.php"
dev_mode_view = 0 # 0 = off | 1 = on - without front Page, only grade view
dev_mode_mail = 0 # 0 = off | 1 = on - no credetials for Debug Mail Server

#===============================================================================

#-------------------------------------------------------------------------------
#                   Skript - dont touch a running system
#-------------------------------------------------------------------------------

def main():
    print("   _____               _         _____                    _           ")
    print("  / ____|             | |       / ____|                  | |          ")
    print(" | |  __ _ __ __ _  __| | ___  | |     _ __ __ ___      _| | ___ _ __ ")
    print(" | | |_ | '__/ _` |/ _` |/ _ \\ | |    | '__/ _` \\ \\ /\\ / / |/ _ \\ '__|")
    print(" | |__| | | | (_| | (_| |  __/ | |____| | | (_| |\\ V  V /| |  __/ |   ")
    print("  \\_____|_|  \\__,_|\\__,_|\\___|  \\_____|_|  \\__,_| \\_/\\_/ |_|\\___|_|   ")
    print("                                                   Copyright by Kr3b5")
    print("\n> Starting... \n")

    if(use_wizard == True):
        init_wizard()

    idle_print = 1

    while True:
        this_hour = datetime.now().hour
        #check if time is in range -> reduce traffic
        if(is_online(this_hour)):
            # get web content
            html_source = get_content()
            #get grade list from html_source
            grade_list = get_grade(html_source)
            #get old grade list
            old_grade_list = get_list()
            #compare both for new grades
            compare(grade_list, old_grade_list)
            #reduce output idle
            idle_print = 1
        else:
            if(idle_print == 1 ):
                print(f"> Idle - next check:{start_time}:00\n")
                idle_print = 0
        sleep(delay)


def init_wizard():
    print("> Start Init Wizard... \n")
    # Credentials DHGE-Service
    matnr = input(">> Matrikelnummer: ")
    passw = getpass.getpass(prompt='>> Passwort: ')
    semester = int(input(">> Semester(1-6): "))
    print("----------------------------------------------------------")
    #Delay Check / Online Time
    delay = int(input(">> In welchen Minutentakt checken: "))*60   #1min = 60
    print("----------------------------------------------------------")
    #SMTP Server (Mail)
    if( input(">> Aktiviere Mail (True/False): ").lower() == 'true'):
        want_Mail = True
    else:
        want_Mail = False
    if(want_Mail == True):
        port = int(input(">> SMTP Server Port: "))
        smtp_server = input(">> SMTP Server Adresse: ")
        login = input(">> Loginname: ")
        password = getpass.getpass(prompt='>> Passwort: ')
        # Mail Content
        sender = input(">> Sendername: ")
        receiver = input(">> Empfänger: ")
        subject = input(">> Betreff: ")
    print("Setup complete! Start crawler...\n")


def is_online(time):
    if( time >= start_time and time < end_time ):
        return True
    else:
        return False


def get_content():
    driver = webdriver.Firefox()
    driver.get(url_dhge)

    if( dev_mode_view == 0 ):
        username = driver.find_element_by_name("matrnr")
        username.clear()
        username.send_keys(matnr)
        password = driver.find_element_by_name("passw")
        password.clear()
        password.send_keys(passw)
        select_element = Select(driver.find_element_by_name("sem"))
        select_element.select_by_value(str(semester))
        driver.find_element_by_xpath("//input[@value='Notenauskunft (Bildschirm)']").click()

    html_source = driver.page_source
    driver.close()

    return html_source


def get_grade( html_source ):
    grade_list = []

    s1 = html_source.split("<tr>")
    for i in range(9):
        del s1[0]

    anz = 0
    for i in range(len(s1)):
        if( s1[i] == "<td colspan=\"9\"><hr></td></tr>" ):
            anz = i

    for i in range(anz):
        s2 = s1[i].split("<td align=\"left\">")
        fach = s2[1].split("</td>")
        fach = fach[0]
        note = s2[1].split("<td align=\"center\">")
        note = note[1].split("                           </td>")
        note = note[0]
        if note.endswith('</td>'):
            note = note[:-5]
        grade_list.append(fach)
        grade_list.append(note)

    return (grade_list)


def write_file(grade_list):
    with open(file_name, 'w') as f:
        for item in grade_list:
            f.write("%s\n" % item)


def get_list():
    try:
        return [line.rstrip('\n') for line in open(file_name, 'r')]
    except FileNotFoundError:
        return "[]"


def compare(grade_list, old_grade_list):
    if(isinstance(old_grade_list, str)):
        print("> First init run!")
        write_file(grade_list)
        print("\nGradelist (new):")
        print(grade_list)
        print("")
    elif(grade_list == old_grade_list):
        print("> No new grades available!")
        print("\nGradelist (old|new):")
        print(old_grade_list)
        print("")
    else:
        print("> New grades available!")
        write_file(grade_list)
        print("\nGradelist (old|new):")
        print(old_grade_list)
        print(grade_list)
        print("")
        if( want_Mail ):
            send_mail(grade_list)


def send_mail(grade_list):
    print(f"> Send mail to {receiver}...")
    message = f"""\
    Subject: {subject}
    To: {receiver}
    From: {sender}
    {str(grade_list)}"""
    try:
      with smtplib.SMTP(smtp_server, port) as server:
        if( dev_mode_mail == 0 ):
            server.login(login, password)
        server.sendmail(sender, receiver, message)
    except (gaierror, ConnectionRefusedError):
      print('> Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
      print('> Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
      print('> SMTP error occurred: ' + str(e))
    else:
      print('> Success')
    print("")




if __name__ == '__main__':
    main()
