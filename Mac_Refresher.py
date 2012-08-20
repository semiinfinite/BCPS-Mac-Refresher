#!/usr/bin/python

import easygui as eg
import dateutil.parser as dparser
import os, sys, time, getpass
import shutil, errno

def startWizard():
    msg = "Welcome to the BCPS Mac Refresher. This application will walk you through the creation of a package that can be used to modify a user back to specific preferences."
    title = "BCPS Mac Refresher"
    wizardOptions = ["Begin", "Quit"]

    selectedWizardOption = eg.indexbox(msg, title, wizardOptions)

    return selectedWizardOption

def selectUser():
    msg = "Please select the user you will be modifying."
    title = "User Selection"

    usersFolder = os.listdir("/Users")
    systemUsers = []
    for user in usersFolder:
        if user == ".localized" or user == "Shared" or user == "Guest":
            continue
        else:
            systemUsers.append(user)

    return eg.choicebox(msg, title, systemUsers)

def moveDesktopYesNo(userName):
    msg = "Would you like to move the desktop items for %s or delete them?" % userName
    title = "Desktop Cleanup"
    choices = ["Move", "Delete"]

    return eg.ynbox(msg, title, choices)

def setBrowserHomepage():
    msg = "What would you like the homepage of the system browsers to be?"
    title = "Browser Homepage Selection"
    default = "http://beep.browardschools.com"

    return eg.enterbox(msg, title, default)

def setPowerMangement():
    msg = "Would you like to set startup and shutdown times?"
    title = "Configure Power Management"

    pmYesNo = eg.ynbox(msg, title)
    if pmYesNo == 0:
        return

    times = []
    msg = "What time do you want the computers to turn on?"
    title = "Startup Time"
    while 1:
        try:
            startup_time = eg.enterbox(msg, title)
            if startup_time != None:
                startup_time = dparser.parse(startup_time)
                startup_time = startup_time.strftime('%H:%M:%S')
                times.append(startup_time)
                break
        except ValueError:
            eg.msgbox("Wrong Time Format.", "Error")
            continue

        if startup_time == None:
            no_startup_time = eg.ynbox("Skip setting a startup time?")
            if no_startup_time == 1:
                times.append("no_startup")
                break
            else:
                continue

    msg = "What time do you want the computers to turn off?"
    title = "Shutdown Time"
    while 1:
        try:
            shutdown_time = eg.enterbox(msg, title)
            if shutdown_time != None:
                shutdown_time = dparser.parse(shutdown_time)
                shutdown_time = shutdown_time.strftime('%H:%M:%S')
                times.append(shutdown_time)
                break
        except ValueError:
            eg.msgbox("Wrong Time Format.", "Error")
            continue
        
        if startup_time == None:
            no_shutdown_time = eg.ynbox("Skip setting a shutdown time?")
            if no_shutdown_time == 1:
                times.append("no_shutdown")
                break
            else:
                continue

    return times

def copyAnything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise

def createPackage(selected_user, move_yes_no, homepage, powermanagement_times):
    copyAnything("BCPS_Mac_Refresher-1.0.pkg/", "/Users/%s/Desktop/BCPS_Mac_Refresher_%s.pkg/" % (getpass.getuser(), selected_user))

    postflight = "/Users/%s/Desktop/BCPS_Mac_Refresher_%s.pkg/Contents/Resources/postflight" % (getpass.getuser(), selected_user)
    dir = os.path.dirname(postflight)

    if not os.path.exists(dir):
        os.makedirs(dir)

    f = open(postflight, 'w')
    f.write("#!/bin/bash\n\n")
    f.write("user = %s\n" % selected_user)
    f.write("move_yes_no = %s\n" % move_yes_no)
    f.write("homepage = %s\n" % homepage)
    f.write('startup = "%s"\n' % powermanagement_times[0])
    f.write('shutdown = "%s"\n' % powermanagement_times[1])
    f.write(r"""
# Move or delete files from selected user
if [[ $move_yes_no == 1 ]]; then
    # move
    mkdir -p /Users/{$user}/Documents/Student\ Files/
    mv /Users/{$user}/Desktop/* /Users/{$user}/Documents/Student\ Files/
else
    # delete
    rm -rf /Users/{$user}/Desktop/*
fi

# Set homepage for Firefox and Safari
# Firefox
sed -i 's|\("browser.startup.homepage",\) "\(.*\)"|\1 "${homepage}"|' /Users/{$user}/Library/Application Support/Firefox/*.default/prefs.js
# Safari
defaults write com.apple.Safari HomePage "{$homepage}"
defaults write com.apple.internetconfigpriv WWWHomePage "{$homepage}"

# Power Management Settings
# Battery
pmset -b sleep 10 displaysleep 5
# Charger
pmset -c sleep 30 displaysleep 0
# UPS
pmset -b sleep 10 displaysleep 5
# Set startup time
sudo pmset repeat wakeorpoweron MTWRF $startup
# Set shutdown time
sudo pmset repeat shutdown MTWRFSU $shutdown
""")
    f.close()

if __name__ == '__main__':
    while True:
        selectedMenuItem = startWizard()
        if selectedMenuItem == 0:
            selected_user = selectUser()
            move_yes_no = moveDesktopYesNo(selected_user)
            homepage = setBrowserHomepage()
            powermanagement_times = setPowerMangement()
            createPackage(selected_user, move_yes_no, homepage, powermanagement_times)
        if selectedMenuItem == 1:
            sys.exit(0)