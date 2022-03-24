import schedule
import time
import os

def job():
    sudoPassword = ''
    command = 'make backup'
    os.system(f'echo {sudoPassword}|sudo -S {command}')

    print("backup done")
    

schedule.every().day.at("22:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
