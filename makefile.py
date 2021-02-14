import schedule
import time
import subprocess
import os

def job():
    sudoPassword = ''
    command = 'make backup'
    os.system('echo %s|sudo -S %s' % (sudoPassword, command))

    print("backup done")
    

schedule.every().day.at("22:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)



