#!/usr/bin/env python3

import os
import subprocess
import json
import sys
from jinja2 import Environment, FileSystemLoader

from collections import defaultdict


def get_tasks():
    # Run the `task export` command to get all tasks in JSON format
    output = subprocess.check_output(["task", "export"], text=True)
    tasks = json.loads(output)
    new_tasks = []
#    tasks_by_project = defaultdict(list)
    for task in tasks:
        if 'project' not in task.keys():
            task['project'] = 'Default'
#        tasks_by_project[task['project']].append(task)
        new_tasks.append(task)
    return new_tasks

def main():
    # Determine the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, 'templates')

    # Set up the Jinja2 environment to load from the templates folder
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('task-list.j2')  # Our Jinja2 template file
    tasks = get_tasks()


    # Render the tasks using our Jinja2 template
    rendered_output = template.render(tasks=tasks)

    # Print the result to the console
    print(rendered_output)

if __name__ == "__main__":
    main()



##!/usr/bin/env python3
#
#from jinja2 import Environment, FileSystemLoader
#import os
#
#TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
#env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
#
#template = env.get_template("task-list.j2")
#rendered_output = template.render(var="value")
#print(rendered_output)
#
