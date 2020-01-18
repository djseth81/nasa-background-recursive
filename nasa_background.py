from datetime import datetime
import click
from tools import background, nasa_api
from tools.utils import parse_str_to_date
import os
from subprocess import call
import platform
from pathlib import Path
import re

@click.group()
def nasa_background():
    pass


@nasa_background.command()
@click.option("--date",
              default=None,
              help="Enter the date as a single string in YYYYMMDD or YYYY-MM-DD format." )
@click.option("--auto",
              is_flag=False,
              help="Disables prompts and sets the background automatically if this can successfully be completed." )

def update(date, auto):
    '''Get the newest NASA Picture of the Day and set it as background'''
    # Check if date is passed as argument, set to default (today) otherwise
    if date is None:
        date = datetime.now()
    else:
        date = parse_str_to_date(date)

    try:
        # Download and print information about
        meta_info = nasa_api.get_info(date)
        click.echo(f"Title: {meta_info['title']}\n")
        click.echo(meta_info['explanation'] + "\n")

        # Check if auto is selected, otherwise prompt user to set it as background
        if auto or click.confirm("Do you wish to download this image and set it as background?"):
            # Download and set the background
            file_path = nasa_api.download_image(date)
            background.change_background(file_path, auto)
    except KeyError:
        click.echo(f"Image not found for the selected date {date}. ")
    except Exception as e:
        click.echo("Fatal error encountered, exiting program.")
        click.echo(e)
@nasa_background.command()
def auto ():
    '''Installs program in desired directory and sets timer for atuo running'''
    from crontab import CronTab
    dir_path = str(Path("261Calcs.py").parent.absolute())
    my_cron = CronTab(user=True)

    # Detect operating system and search corresponding directory structure
    if platform.system().lower().startswith('win'):
        bucket = []
        for path,d,f in os.walk("C:\\"):
            for files in f:
                if files == "nasa_background.py":
                    bucket.append(os.path.join(path,files))
        for item in bucket:
            path,file = os.path.split(item)
            i = 0
            while i < len(path)-1:
                path, directory = os.path.split(path)
                if directory == "Desktop":
                    break
                i += 1

    elif platform.system().lower().startswith('lin'):
        bucket = []
        for path,d,f in os.walk("/home/"):
            for files in f:
                if files == "nasa_background.py":
                    bucket.append(os.path.join(path,files))
        for item in bucket:
            path,file = os.path.split(item)
            i = 0
            while i < len(path)-1:
                path, directory = os.path.split(path)
                if directory == "Desktop":
                    break
                i += 1

    elif platform.system().lower().startswith('dar'):
        bucket = []
        for path,d,f in os.walk("/Users/"):
            for files in f:
                if files == "nasa_background.py":
                    bucket.append(os.path.join(path,files))
        for item in bucket:
            path,file = os.path.split(item)
            i = 0
            while i < len(path)-1:
                path, directory = os.path.split(path)
                if path == dir_path:
                    break
                i += 1

    job = my_cron.new(command='python3 '+item+' update')
    timer = str(input("### Input Refresh Rate ###\nFORMAT: MINS:HRS:DAYS:WEEKS:MONTHS\n> "))

    while len(re.findall("[0-99]",timer)) < 2 or re.search(":", timer) == None:
        if  len(re.findall("[0-99]",timer)) < 2 or re.search(":", timer) == None:
            timer = str(input("You mistyped.\nFORMAT: MINS:HRS:DAYS:WEEKS:MONTHS\n> "))
        else:
            break
        
    timer = timer.replace(':',' ').split()
    i = 0
    while i < len(timer):
        if i == 0: #MIN
            if int(timer[i]) == 0:
                job.minutes.on(int(timer[i]))
            else:
                job.minute.every(int(timer[i]))
        if i == 1: #HOUR
            if int(timer[i]) == 0:
                job.hour.on(int(timer[i]))
            else:
                job.hour.every(int(timer[i]))
        if i == 2: #DAY
            if int(timer[i]) == 0:
                job.day.on(1)
            else:
                job.day.every(int(timer[i]))
        if i == 3: #WEEK
            if int(timer[i]) == 0:
                job.day.on(1)
            else:
                if int(timer[i]) > 0 and int(timer[i]) < 4:
                    job.day.every((int(timer[i])*7))
                else:
                    job.month.every(1)
        if i == 4: #MONTH
            if int(timer[i]) == 0:
                job.month.on(1)
            else:
                job.month.every(int(timer[i]))
        i += 1
    
    my_cron.write()

if __name__ == '__main__':
    nasa_background()
