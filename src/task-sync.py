#!/usr/bin/env python3

import configparser
import os
import subprocess
import json
import sys
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from markdown_it import MarkdownIt
from collections import defaultdict

config_filename = Path.home() / ".config" / "obsidian-taskwarrior-bridge" / "config.ini"

config = configparser.ConfigParser()
config["DEFAULT"] = {"output_file": "/tmp/tasks.md"}


def get_tw_tasks():
    ''' Return a dict mapping project names to lists of tasks in that project in Taskwarrior. '''
    output = subprocess.check_output(
        ["task", "status.not:completed", "export"], text=True
    )
    tasks = json.loads(output)
    tasks_by_project = defaultdict(list)
    for task in tasks:
        if "project" in task:
            task_project = task["project"]
        else:
            task_project = "default"
        tasks_by_project[task_project].append(task)
    return tasks_by_project


def write_tasks(filename, tasks):
    # Determine the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "templates")

    # Set up the Jinja2 environment to load from the templates folder
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("task-list.j2")  # Our Jinja2 template file

    # Render tasks
    rendered_output = template.render(data=tasks)
    output_path = Path(config["DEFAULT"]["output_file"])
    output_path.write_text(rendered_output, encoding="utf-8")


def read_tasks(filename, tasks):
    # Scan tasks
    md = MarkdownIt()
    tokens = md.parse(Path(filename).read_text())
    current_heading = None
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open":
            current_heading = tokens[i + 1].content  # heading text is always next token
        if current_heading == "New Tasks":
            print(current_heading)
            print(tok.type)
            print(tok)

def main():
    config.read(Path(config_filename))
    # print(config['DEFAULT']['output_file'])

    tasks = get_tw_tasks()

    # Parse task list
    read_tasks(config["DEFAULT"]["output_file"], tasks)

    # filter tasks that have changed state.
    # TODO: Consider only allowing open -> closed in the open tasks list?

    # When detecting new tasks, wait for list of new tasks to have not changed for some period of time
    # to prevent us from creating a task that has only been half-written.

    write_tasks(config["DEFAULT"]["output_file"], tasks)


if __name__ == "__main__":
    main()
