from tkinter import *
import requests
import datetime
import math

# MODIFY HERE
#######################################
authorization = ""  # Enter your ClickUp API in the quotation marks
team_id = ""  # Enter your team ID for the ClickUp Space you want to work with
#######################################

# Creating an application
# pyinstaller CreatingGui2.py -F

end_of_day = datetime.datetime.now().date().strftime('%m/%d/%Y') + ", 23:59:59"
unix_time = datetime.datetime.timestamp(datetime.datetime.strptime(end_of_day,
                                                                   "%m/%d/%Y, %H:%M:%S")) * 1000

# This one uses tkinter to create a GUI application for schedule
window = Tk()
window.title("Time Management")
window.configure(background="black")

# Designate Height and Width of our App
app_width = 370
app_height = 310

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width / 2) - (app_width / 2)
y = (screen_height / 2) - (app_height / 2)
window.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

frame2 = Frame(window)
frame2.grid(row=1, column=0, sticky="nsew")

window.resizable(width=False, height=False)

date_today = datetime.datetime.now().date().strftime('%m/%d/%Y')
end_time = "23:59"
objective = "left"

output = Text(frame2, width=30, height=13, wrap=WORD, background="black", fg="white", font=("Arial", 20))
output.grid(row=5, column=0)
output.tag_config('cyan', foreground="cyan")
output.tag_config('red', foreground="red")
output.tag_config('white', foreground="white")
output.tag_config('lime_green', foreground="lime green")
output.tag_config('magenta', foreground="magenta")
output.tag_config('yellow', foreground="yellow")
output.tag_config('orange', foreground="orange")
output.tag_config('silver', foreground="silver")


class Folder:
    def __init__(self, folder_name, time_estimate, due_date, daily_hours, early_time_estimate, early_due_date):
        self.folder_name = folder_name
        self.time_estimate = time_estimate
        self.due_date = due_date
        self.daily_hours = daily_hours
        self.early_time_estimate = early_time_estimate
        self.early_due_date = early_due_date


def find_time(event, event_name):
    #   It's separated by color
    headers = {
        'Authorization': authorization,
        'Content-Type': 'application/json'
    }

    speedrun = ""
    speedrun_time = 0
    total = 0
    grouped_tasks = 0
    total2 = 0
    page = 0
    time_spent = 0
    task_list = []

    #   Only retrieves active tasks
    present_time = int(datetime.datetime.now().timestamp() * 1000)
    while True:
        # Retrieve tasks that have a due date greater than the present time including subtasks
        # Improves performance from 40 seconds to around 5 seconds, so I don't need to wait long to get results.
        task_request = requests.get(
            'https://api.clickup.com/api/v2/team/' + team_id + '/task?&subtasks=true&due_date_gt=' + str(
                present_time) + '&page=' + str(page),
            headers=headers).json()['tasks']
        if len(task_request) == 100:
            page += 1
            for j in task_request:
                task_list.append(j)
        elif len(task_request) > 0:
            for j in task_request:
                task_list.append(j)
            break
        else:
            break

    get_running_task = requests.get(
        'https://api.clickup.com/api/v2/team/' + team_id + '/time_entries/current?assignee=',
        headers=headers).json()['data']

    #   Priority Tasks
    running_task_estimate = 0
    current_task = 0
    matching_name = None
    if get_running_task is None:
        get_running_task = {'duration': 0, "task": {"name": " "}, 'time_estimate': 0}

        current_task = (get_running_task['duration'] + get_running_task['time_estimate']) / 1000 / 60 / 60
        running_task_estimate = get_running_task['time_estimate'] / 1000 / 60 / 60

        a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
        b1 = "No Task Running"
        output.insert(INSERT, a1 + b1 + '\n', 'silver')
    else:
        for i in task_list:
            if get_running_task['task']['name'] == i['name']:
                matching_name = next((item['name'] for item in i['tags'] if item['name'] in
                                      ['1', '2', '3', '4', '5', '6', '7', '8', '9']), None)
                break

    folders = []
    for i in task_list:
        if i["priority"] is not None and i["priority"]["priority"] == "urgent":
            if i['time_estimate'] is not None:
                folder_not_found = True
                if len(folders) == 0:
                    temp1 = i['time_estimate']

                    if get_running_task is not None and get_running_task['task']['name'] == i['name']:
                        try:
                            if abs(get_running_task['duration'] - i['time_spent']) < i['time_estimate']:
                                temp1 += get_running_task['duration'] - i['time_spent']
                            else:
                                temp1 -= i['time_estimate']
                        except KeyError:
                            if abs(get_running_task['duration']) < i['time_estimate']:
                                temp1 += get_running_task['duration']
                            else:
                                temp1 -= i['time_estimate']
                    else:
                        try:
                            if i['time_spent'] <= i['time_estimate']:
                                temp1 -= i['time_spent']
                            else:
                                temp1 -= i['time_estimate']
                        except KeyError:
                            pass

                    folders.append(Folder(i['folder']['name'].split(":")[0],
                                          temp1,
                                          i['due_date'],
                                          i['folder']['name'].split(":")[1],
                                          temp1,
                                          i['due_date']))
                else:
                    for j in folders:
                        if i['folder']['name'].split(":")[0] == j.folder_name:
                            j.time_estimate += i['time_estimate']

                            if get_running_task is not None and get_running_task['task']['name'] == i['name']:
                                try:
                                    if abs(get_running_task['duration'] - i['time_spent']) < i['time_estimate']:
                                        j.time_estimate += get_running_task['duration'] - i['time_spent']
                                    else:
                                        j.time_estimate -= i['time_estimate']
                                except KeyError:
                                    if abs(get_running_task['duration']) < i['time_estimate']:
                                        j.time_estimate += get_running_task['duration']
                                    else:
                                        j.time_estimate -= i['time_estimate']
                            else:
                                try:
                                    if i['time_spent'] <= i['time_estimate']:
                                        j.time_estimate -= i['time_spent']
                                    else:
                                        j.time_estimate -= i['time_estimate']
                                except KeyError:
                                    pass

                            if j.due_date < i['due_date']:
                                j.due_date = i['due_date']

                            if j.early_due_date > i['due_date']:
                                j.early_time_estimate = i['time_estimate']

                                if get_running_task is not None and get_running_task['task']['name'] == i['name']:
                                    try:

                                        if abs(get_running_task['duration'] - i['time_spent']) <= i['time_estimate']:
                                            j.early_time_estimate += get_running_task['duration'] - i['time_spent']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                    except KeyError:
                                        if abs(get_running_task['duration']) < i['time_estimate']:
                                            j.early_time_estimate += get_running_task['duration']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                else:
                                    try:
                                        if i['time_spent'] <= i['time_estimate']:
                                            j.early_time_estimate -= i['time_spent']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                    except KeyError:
                                        pass

                                j.early_due_date = i['due_date']

                            elif j.early_due_date == i['due_date']:
                                j.early_time_estimate += i['time_estimate']

                                if get_running_task is not None and get_running_task['task']['name'] == i['name']:
                                    try:
                                        if abs(get_running_task['duration'] - i['time_spent']) < i['time_estimate']:
                                            j.early_time_estimate += get_running_task['duration'] - i['time_spent']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                    except KeyError:
                                        if abs(get_running_task['duration']) < i['time_estimate']:
                                            j.early_time_estimate += get_running_task['duration']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                else:
                                    try:
                                        if i['time_spent'] <= i['time_estimate']:
                                            j.early_time_estimate -= i['time_spent']
                                        else:
                                            j.early_time_estimate -= i['time_estimate']
                                    except KeyError:
                                        pass

                            folder_not_found = False
                    if folder_not_found:
                        temp1 = i['time_estimate']

                        if get_running_task is not None and get_running_task['task']['name'] == i['name']:
                            try:
                                if abs(get_running_task['duration'] - i['time_spent']) < i['time_estimate']:
                                    temp1 += get_running_task['duration'] - i['time_spent']
                                else:
                                    temp1 -= i['time_estimate']
                            except KeyError:
                                if abs(get_running_task['duration']) < i['time_estimate']:
                                    temp1 += get_running_task['duration']
                                else:
                                    temp1 -= i['time_estimate']
                        else:
                            try:
                                if i['time_spent'] <= i['time_estimate']:
                                    temp1 -= i['time_spent']
                                else:
                                    temp1 -= i['time_estimate']
                            except KeyError:
                                pass

                        folders.append(Folder(i['folder']['name'].split(":")[0],
                                              temp1,
                                              i['due_date'],
                                              i['folder']['name'].split(":")[1],
                                              temp1,
                                              i['due_date']))

        if i['tags'] is not None and len(i['tags']) > 0 and i['tags'][0]['name'] == 'speedrun':
            speedrun_time = datetime.datetime.fromtimestamp(int(i['due_date']) / 1000).timestamp()
            dt = datetime.datetime.fromtimestamp(int(i['due_date']) / 1000)
            dt = dt.strftime('%m/%d/%Y, %H:%M')
            event = dt
            speedrun = "(" + dt[:5] + ") "

        if i['tags'] is not None and len(i['tags']) > 0 and any(item['name'] == 'today' for item in i['tags']):
            if i['time_estimate'] is not None:
                total += i['time_estimate']
                try:
                    if i['time_spent'] <= i['time_estimate']:
                        total -= i['time_spent']
                    else:
                        total -= i['time_estimate']
                except KeyError:
                    pass

            ## This code runs to find tasks
            if matching_name is not None and any(item['name'] == matching_name for item in i['tags']):
                if i['time_estimate'] is not None:
                    grouped_tasks += i['time_estimate']
                    try:
                        if i['time_spent'] <= i['time_estimate']:
                            grouped_tasks -= i['time_spent']
                        else:
                            grouped_tasks -= i['time_estimate']
                    except KeyError:
                        pass

            if get_running_task['task']['name'] == i['name']:
                if matching_name is None:
                    if i['time_estimate'] is not None:
                        grouped_tasks += i['time_estimate']
                        try:
                            if i['time_spent'] <= i['time_estimate']:
                                grouped_tasks -= i['time_spent']
                            else:
                                grouped_tasks -= i['time_estimate']
                        except KeyError:
                            pass
                task_string = "Task: " + str(i['name'])

                if i['parent'] is not None:
                    for parent in task_list:
                        if parent['id'] == i['parent']:
                            task_string += " (" + str(parent['name']) + ')'

                output.insert(INSERT, task_string + '\n\n', 'white')

                try:
                    time_spent -= i['time_spent']

                    current_task = (get_running_task['duration'] + i['time_estimate'] - i[
                        'time_spent']) / 1000 / 60 / 60
                    running_task_estimate = (i['time_estimate']) / 1000 / 60 / 60
                except KeyError:
                    current_task = (get_running_task['duration'] + i['time_estimate']) / 1000 / 60 / 60
                    running_task_estimate = (i['time_estimate']) / 1000 / 60 / 60

                if current_task > 2:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(math.trunc(current_task)) + "hrs " + str(
                        math.trunc((current_task % 1) * 60)) + "mins left for task"
                    output.insert(INSERT, a1 + b1 + '\n', 'cyan')
                elif current_task > 1:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(math.trunc(current_task)) + "hr " + str(
                        math.trunc((current_task % 1) * 60)) + "mins left for task"
                    output.insert(INSERT, a1 + b1 + '\n', 'cyan')
                elif current_task > 0:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(math.trunc((current_task % 1) * 60)) + "mins left for task"
                    output.insert(INSERT, a1 + b1 + '\n', 'cyan')
                elif current_task > -1:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(abs(math.trunc(current_task * 60))) + "mins over task"
                    output.insert(INSERT, a1 + b1 + '\n', 'red')
                elif current_task > -2:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(math.trunc(abs(current_task))) + "hr " + str(
                        math.trunc((abs(current_task) % 1) * 60)) + "mins over task"
                    output.insert(INSERT, a1 + b1 + '\n', 'red')
                elif current_task <= -2:
                    a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
                    b1 = str(math.trunc(abs(current_task))) + "hrs " + str(
                        math.trunc((abs(current_task) % 1) * 60)) + "mins over task"
                    output.insert(INSERT, a1 + b1 + '\n', 'red')

    start_time = datetime.datetime.today().strftime('%m/%d/%Y, 23:59:59')
    start = int(datetime.datetime.strptime(start_time, "%m/%d/%Y, %H:%M:%S").timestamp() * 1000)

    total2 = total2 / 1000 / 60 / 60

    dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    time_until_midnight = str(datetime.datetime.combine(tomorrow, datetime.time.min) - dt)
    time_array = time_until_midnight.split(":")

    special_time_utc = int(datetime.datetime.strptime(end_of_day, "%m/%d/%Y, %H:%M:%S").timestamp())
    current_time = int(datetime.datetime.now().timestamp())

    if speedrun_time > 0:
        time_difference = (speedrun_time - current_time) / 60 / 60
    else:
        time_difference = (special_time_utc - current_time) / 60 / 60

    a = total / 1000 / 60 / 60  # time for work
    grouped_tasks = grouped_tasks / 1000 / 60 / 60  # time for group work
    time_spent_hrs = time_spent / 1000 / 60 / 60

    # Finding time speedrun is set
    def end_time():
        if time_difference > 2:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(math.trunc(time_difference)) + "hrs " + str(
                math.trunc((time_difference % 1) * 60)) + "mins left"
            output.insert(INSERT, a1 + b1 + '\n', 'silver')
        elif time_difference > 1:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(math.trunc(time_difference)) + "hr " + str(
                math.trunc((time_difference % 1) * 60)) + "mins left"
            output.insert(INSERT, a1 + b1 + '\n', 'silver')
        elif time_difference > 0:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(math.trunc((time_difference % 1) * 60)) + "mins left"
            output.insert(INSERT, a1 + b1 + '\n', 'silver')
        elif time_difference > -1:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(abs(math.trunc(time_difference * 60))) + "mins past " + event_name
            output.insert(INSERT, a1 + b1 + '\n', 'red')
        elif time_difference > -2:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(math.trunc(abs(time_difference))) + "hr " + str(
                math.trunc((abs(time_difference) % 1) * 60)) + "mins past " + event_name
            output.insert(INSERT, a1 + b1 + '\n', 'red')
        elif time_difference <= -2:
            a1 = speedrun + datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
            b1 = str(math.trunc(abs(time_difference))) + "hrs " + str(
                math.trunc((abs(time_difference) % 1) * 60)) + "mins past " + event_name
            output.insert(INSERT, a1 + b1 + '\n', 'red')

    # Calculating appropriate time required
    def time_required(work_time):
        if current_task > 0:
            spare_time = time_difference - work_time - get_running_task['duration'] / 1000 / 60 / 60
        else:
            if abs(time_spent_hrs) < running_task_estimate:
                spare_time = time_difference - work_time + running_task_estimate + time_spent_hrs
            else:
                spare_time = time_difference - work_time

        if spare_time > 0:
            if current_task > 0:
                if work_time + get_running_task['duration'] / 1000 / 60 / 60 >= 2:
                    a1 = (datetime.datetime.now() + datetime.timedelta(
                        hours=work_time + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                    output.insert(INSERT, a1, 'lime_green')
                    b1 = str(math.trunc(work_time + get_running_task['duration'] / 1000 / 60 / 60)) + "hrs " + str(
                        math.trunc(((work_time + get_running_task['duration'] / 1000 / 60 / 60) % 1) * 60)) + "mins required"
                    output.insert(INSERT, b1 + '\n', 'lime_green')
                elif work_time + get_running_task['duration'] / 1000 / 60 / 60 >= 1:
                    a1 = (datetime.datetime.now() + datetime.timedelta(
                        hours=work_time + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                    output.insert(INSERT, a1, 'lime_green')
                    b1 = str(math.trunc(work_time + get_running_task['duration'] / 1000 / 60 / 60)) + "hr " + str(
                        math.trunc(((work_time + get_running_task['duration'] / 1000 / 60 / 60) % 1) * 60)) + "mins required"
                    output.insert(INSERT, b1 + '\n', 'lime_green')
                elif work_time + get_running_task['duration'] / 1000 / 60 / 60 >= 0:
                    a1 = (datetime.datetime.now() + datetime.timedelta(
                        hours=work_time + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                    output.insert(INSERT, a1, 'lime_green')
                    b1 = str(math.trunc(((work_time + get_running_task['duration'] / 1000 / 60 / 60) % 1) * 60)) + "mins required"
                    output.insert(INSERT, b1 + '\n', 'lime_green')
            elif current_task <= 0:
                if abs(time_spent_hrs) < running_task_estimate:
                    if work_time - running_task_estimate - time_spent_hrs >= 2:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time - running_task_estimate - time_spent_hrs)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc(work_time - running_task_estimate - time_spent_hrs)) + "hrs " + str(
                            math.trunc(((work_time - running_task_estimate - time_spent_hrs) % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')
                    elif work_time - running_task_estimate - time_spent_hrs >= 1:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time - running_task_estimate - time_spent_hrs)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc(work_time - running_task_estimate - time_spent_hrs)) + "hr " + str(
                            math.trunc(((work_time - running_task_estimate - time_spent_hrs) % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')
                    elif work_time - running_task_estimate - time_spent_hrs >=0:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time - running_task_estimate - time_spent_hrs)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc(((work_time - running_task_estimate - time_spent_hrs) % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')
                else:
                    if work_time >= 2:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc(work_time)) + "hrs " + str(
                            math.trunc((work_time % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')
                    elif work_time >= 1:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc(work_time)) + "hr " + str(
                            math.trunc((work_time % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')
                    elif work_time >= 0:
                        a1 = (datetime.datetime.now() + datetime.timedelta(
                            hours=work_time)).strftime(
                            "%I:%M %p") + " : "
                        output.insert(INSERT, a1, 'lime_green')
                        b1 = str(math.trunc((work_time % 1) * 60)) + "mins required"
                        output.insert(INSERT, b1 + '\n', 'lime_green')

            if spare_time >= 2:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
                b1 = str(math.trunc(spare_time)) + "hrs " + str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
                output.insert(INSERT, b1 + '\n', 'magenta')
            elif spare_time >= 1:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
                b1 = str(math.trunc(spare_time)) + "hr " + str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
                output.insert(INSERT, b1 + '\n', 'magenta')
            else:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
                b1 = str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
                output.insert(INSERT, b1 + '\n', 'magenta')
        else:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=work_time + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                output.insert(INSERT, a1, 'red')
                b1 = str(math.trunc(work_time + get_running_task['duration'] / 1000 / 60 / 60)) + "hrs " + str(
                    math.trunc(((work_time + get_running_task['duration'] / 1000 / 60 / 60) % 1) * 60)) + "mins required"
                output.insert(INSERT, b1 + '\n', 'red')
            elif current_task <= 0:
                if abs(time_spent_hrs) < running_task_estimate:
                    a1 = (datetime.datetime.now() + datetime.timedelta(
                        hours=work_time - running_task_estimate - time_spent_hrs)).strftime("%I:%M %p") + " : "
                    output.insert(INSERT, a1, 'red')
                    b1 = str(math.trunc(work_time - running_task_estimate - time_spent_hrs)) + "hrs " + str(
                        math.trunc(((work_time - running_task_estimate - time_spent_hrs) % 1) * 60)) + "mins required"
                    output.insert(INSERT, b1 + '\n', 'red')
                else:
                    a1 = (datetime.datetime.now() + datetime.timedelta(
                        hours=work_time)).strftime("%I:%M %p") + " : "
                    output.insert(INSERT, a1, 'red')
                    b1 = str(math.trunc(work_time)) + "hrs " + str(
                        math.trunc((work_time % 1) * 60)) + "mins required"
                    output.insert(INSERT, b1 + '\n', 'red')
            a1 = str(math.trunc(spare_time * -1)) + "hrs " + str(
                math.trunc(((spare_time * -1) % 1) * 60)) + "mins behind schedule"
            output.insert(INSERT, a1 + '\n', 'red')

    time_required(grouped_tasks)
    output.insert(INSERT, "-------------------------------------------------\n", 'white')
    time_required(a)
    output.insert(INSERT, "-------------------------------------------------\n", 'white')
    end_time()

# Gives total for tasks
    total_hours_per_day = 0
    total_hours_needed = 0
    total_hours_goal = 0
    total_hours_added = 0
    for i in folders:
        # Might be a rounding error somewhere here?
        i.time_estimate = round(i.time_estimate / 1000 / 60 / 60, 2)
        i.due_date = round((int(i.due_date) - present_time) / 1000 / 60 / 60 / 24, 10)

        i.early_time_estimate = round(i.early_time_estimate / 1000 / 60 / 60, 2)
        i.early_due_date = round((int(i.early_due_date) - present_time) / 1000 / 60 / 60 / 24, 10)

        output.insert(INSERT, "\n" + str(i.folder_name) + "\n", 'yellow')
        output.insert(INSERT, str(i.time_estimate) + 'hrs in ' + str(math.ceil(i.due_date))
                      + "days (" + str(round(i.time_estimate / math.ceil(i.due_date), 2)) + "hrs/day)\n", 'yellow')

        if i.due_date != i.early_due_date:
            output.insert(INSERT, str(i.early_time_estimate) + 'hrs in ' + str(math.ceil(i.early_due_date))
                          + "days (" + str(round(i.early_time_estimate / math.ceil(i.early_due_date), 2)) + "hrs/day)\n", 'yellow')

            if i.early_time_estimate / i.early_due_date > i.time_estimate / i.due_date:

                total_hours_per_day += round(i.early_time_estimate / math.ceil(i.early_due_date), 2)
                total_hours_needed += round(float(i.daily_hours) * math.floor(i.early_due_date) - i.early_time_estimate, 2)
                total_hours_goal += round(float(i.daily_hours), 2)
                total_hours_added += round(i.early_time_estimate, 2)

                if i.early_time_estimate / i.early_due_date < 24:
                    if float(i.daily_hours) * math.floor(i.early_due_date) - i.early_time_estimate >= 0:
                        output.insert(INSERT,
                                      str(round(float(i.daily_hours) * math.floor(i.early_due_date) -
                                                i.early_time_estimate, 2))
                                      + 'hrs free for '
                                      + str(i.daily_hours) + 'hrs/day goal\n', 'lime_green')
                    else:
                        output.insert(INSERT,
                                      str(round(float(i.daily_hours) * math.floor(i.early_due_date) -
                                                i.early_time_estimate, 2))
                                      + 'hrs free for '
                                      + str(i.daily_hours) + 'hrs/day goal\n', 'orange')
                else:
                    output.insert(INSERT,
                                  str(round(i.early_time_estimate - i.early_due_date * 24, 2)) + "hrs over time\n",
                                  'red')
            else:

                total_hours_per_day += round(i.time_estimate / math.ceil(i.due_date), 2)
                total_hours_needed += round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate,2)
                total_hours_goal += round(float(i.daily_hours), 2)
                total_hours_added += round(i.time_estimate, 2)

                if i.time_estimate / i.due_date < 24:
                    if float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate >= 0:
                        output.insert(INSERT,
                                      str(round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate, 2))
                                      + 'hrs free for '
                                      + str(i.daily_hours) + 'hrs/day goal\n', 'lime_green')
                    else:
                        output.insert(INSERT,
                                      str(round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate, 2))
                                      + 'hrs free for '
                                      + str(i.daily_hours) + 'hrs/day goal\n', 'orange')
                else:
                    output.insert(INSERT, str(round(i.time_estimate - i.due_date * 24, 2)) + "hrs over time\n", 'red')
        else:

            total_hours_per_day += round(i.time_estimate / math.ceil(i.due_date), 2)
            total_hours_needed += round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate, 2)
            total_hours_goal += round(float(i.daily_hours), 2)
            total_hours_added += round(i.time_estimate, 2)

            if i.time_estimate / i.due_date < 24:
                if float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate >= 0:
                    output.insert(INSERT, str(round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate, 2))
                                  + 'hrs free for '
                                  + str(i.daily_hours) + 'hrs/day goal\n', 'lime_green')
                else:
                    output.insert(INSERT, str(round(float(i.daily_hours) * math.floor(i.due_date) - i.time_estimate, 2))
                                  + 'hrs free for '
                                  + str(i.daily_hours) + 'hrs/day goal\n', 'orange')
            else:
                output.insert(INSERT, str(round(i.time_estimate - i.due_date * 24, 2)) + "hrs over time\n", 'red')

    output.insert(INSERT, "\nTotal\n" + str(round(total_hours_added, 2)) + "hrs for " + str(round(total_hours_per_day, 2)) +
                  'hrs/day minimum\n' + str(round(total_hours_needed, 2)) + "hrs free for " +
                  str(round(total_hours_goal, 2)) + 'hrs/day goal', 'silver')


entered_text = date_today + ", " + end_time
entered_text2 = objective
output.delete(0.0, END)
find_time(entered_text, entered_text2)

window.mainloop()
