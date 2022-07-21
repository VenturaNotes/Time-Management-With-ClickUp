from tkinter import *
import requests
import datetime
import math

# MODIFY HERE
#######################################
authorization = ""  # Enter your ClickUp API in the quotation marks
team_id = ""  # Enter your team ID for the ClickUp Space you want to work with
#######################################


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
app_height = 145  # taller?

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

output = Text(frame2, width=30, height=6, wrap=WORD, background="black", fg="white", font=("Arial", 20))
output.grid(row=5, column=0)
output.tag_config('cyan', foreground="cyan")
output.tag_config('red', foreground="red")
output.tag_config('white', foreground="white")
output.tag_config('lime_green', foreground="lime green")
output.tag_config('magenta', foreground="magenta")
output.tag_config('yellow', foreground="yellow")


# NEED TO INCLUDE AUTHORIZATION AND CONTENT_TYPE

def find_time(event, event_name):
    #   It's separated by color
    headers = {
        'Authorization': authorization,
        'Content-Type': 'application/json'
    }

    total = 0
    total2 = 0
    page = 0
    task_list = []

    #   Only retrieves active tasks
    present_time = int(datetime.datetime.now().timestamp() * 1000)
    while True:
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

    if get_running_task is None:
        get_running_task = {'duration': 0, "task": {"name": " "}, 'time_estimate': 0}

        current_task = (get_running_task['duration'] + get_running_task['time_estimate']) / 1000 / 60 / 60
        running_task_estimate = get_running_task['time_estimate'] / 1000 / 60 / 60

        a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task)).strftime("%I:%M %p") + " : "
        b1 = "No Task Running"
        output.insert(INSERT, a1 + b1 + '\n', 'white')

    urgent_time = 0
    urgent_days_left = 1
    for i in task_list:
        if i["priority"] is not None and i["priority"]["priority"] == "urgent":
            if i['time_estimate'] is not None:
                urgent_time += i['time_estimate']
                if urgent_days_left == 1:
                    urgent_days_left = round((int(i['due_date']) - present_time) / 1000 / 60 / 60 / 24, 2)
        # if i['due_date'] is not None and float(i['due_date']) < unix_time:
        if i['tags'] is not None and len(i['tags']) > 0 and i['tags'][0]['name'] == 'today':
            if i['time_estimate'] is not None:
                total += i['time_estimate']
            if get_running_task['task']['name'] == i['name']:

                current_task = (get_running_task['duration'] + i['time_estimate']) / 1000 / 60 / 60
                running_task_estimate = i['time_estimate'] / 1000 / 60 / 60

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

    time_difference = (special_time_utc - current_time) / 60 / 60

    a = total / 1000 / 60 / 60  # time for work

    if abs(get_running_task['duration'] / 1000 / 60 / 60) < running_task_estimate:
        spare_time = time_difference - a - get_running_task['duration'] / 1000 / 60 / 60
    else:
        spare_time = time_difference - a + running_task_estimate

    if time_difference > 2:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(math.trunc(time_difference)) + "hrs " + str(
            math.trunc((time_difference % 1) * 60)) + "mins left"
        output.insert(INSERT, a1 + b1 + '\n', 'white')
    elif time_difference > 1:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(math.trunc(time_difference)) + "hr " + str(
            math.trunc((time_difference % 1) * 60)) + "mins left"
        output.insert(INSERT, a1 + b1 + '\n', 'white')
    elif time_difference > 0:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(math.trunc((time_difference % 1) * 60)) + "mins left"
        output.insert(INSERT, a1 + b1 + '\n', 'white')
    elif time_difference > -1:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(abs(math.trunc(time_difference * 60))) + "mins past " + event_name
        output.insert(INSERT, a1 + b1 + '\n', 'red')
    elif time_difference > -2:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(math.trunc(abs(time_difference))) + "hr " + str(
            math.trunc((abs(time_difference) % 1) * 60)) + "mins past " + event_name
        output.insert(INSERT, a1 + b1 + '\n', 'red')
    elif time_difference <= -2:
        a1 = datetime.datetime.strptime(event.split(", ")[1], "%H:%M").strftime("%I:%M %p") + " : "
        b1 = str(math.trunc(abs(time_difference))) + "hrs " + str(
            math.trunc((abs(time_difference) % 1) * 60)) + "mins past " + event_name
        output.insert(INSERT, a1 + b1 + '\n', 'red')

    # Time difference tells me how much time is left (should be bigger)
    if spare_time > 0:
        if a - running_task_estimate > 2:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + (get_running_task['duration'] / 1000 / 60 / 60) - current_task)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            b1 = str(math.trunc(a - running_task_estimate)) + "hrs " + str(
                math.trunc(((a - running_task_estimate) % 1) * 60)) + "mins required"
            output.insert(INSERT, b1 + '\n', 'lime_green')
        elif a - running_task_estimate >= 1:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + (get_running_task['duration'] / 1000 / 60 / 60) - current_task)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            b1 = str(math.trunc(a - running_task_estimate)) + "hr " + str(
                math.trunc(((a - running_task_estimate) % 1) * 60)) + "mins required"
            output.insert(INSERT, b1 + '\n', 'lime_green')
        elif a - running_task_estimate >= 0:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + get_running_task['duration'] / 1000 / 60 / 60)).strftime("%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(
                    hours=a + (get_running_task['duration'] / 1000 / 60 / 60) - current_task)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'lime_green')
            b1 = str(math.trunc(((a - running_task_estimate) % 1) * 60)) + "mins required"
            output.insert(INSERT, b1 + '\n', 'lime_green')
        if spare_time > 2:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task + spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            b1 = str(math.trunc(spare_time)) + "hrs " + str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
            output.insert(INSERT, b1 + '\n', 'magenta')
        elif spare_time > 1:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task + spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            b1 = str(math.trunc(spare_time)) + "hr " + str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
            output.insert(INSERT, b1 + '\n', 'magenta')
        else:
            if current_task > 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=current_task + spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            elif current_task <= 0:
                a1 = (datetime.datetime.now() + datetime.timedelta(hours=spare_time)).strftime(
                    "%I:%M %p") + " : "
                output.insert(INSERT, a1, 'magenta')
            b1 = str(math.trunc((spare_time % 1) * 60)) + "mins of spare time"
            output.insert(INSERT, b1 + '\n', 'magenta')
    else:
        a1 = str(math.trunc(spare_time * -1)) + "hrs " + str(
            math.trunc(((spare_time * -1) % 1) * 60)) + "mins behind schedule"
        output.insert(INSERT, a1 + '\n', 'red')

    urgent_time = round(urgent_time / 1000 / 60 / 60, 2)
    output.insert(INSERT, str(urgent_time) + 'hrs in ' + str(urgent_days_left)
                  + "days (" + str(round(urgent_time / urgent_days_left, 2)) + "hrs/day)\n", 'yellow')
    output.insert(INSERT, str(round(((urgent_days_left * 12) - urgent_time) * 2, 2)) + 'hrs free', 'yellow')


entered_text = date_today + ", " + end_time
entered_text2 = objective
output.delete(0.0, END)
find_time(entered_text, entered_text2)

window.mainloop()
