#!/usr/bin/env python3

import configparser
import os
import subprocess
import json
import sys
import re
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from markdown_it import MarkdownIt
from collections import defaultdict

config_filename = Path.home() / ".config" / "obsidian-taskwarrior-bridge" / "config.ini"

config = configparser.ConfigParser()
config["DEFAULT"] = {
    "output_file": "/tmp/tasks.md",
    "new_tasks_file": "/tmp/newtasks.md",
}

def mark_task_complete(task_uuid):
    """ Mark a taskwarrior task as complete """
    print(f"Marking task as complete: {task_uuid}")
    try:
        output = subprocess.check_output(
            ["task", task_uuid, "done"], text=True
        )
    except subprocess.CalledProcessError as e:
        pass

def get_tw_tasks():
    """Return a dict mapping project names to lists of tasks in that project in Taskwarrior."""
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


def write_markdown(filename, template_filename, data):
    # Determine the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(script_dir, "templates")

    # Set up the Jinja2 environment to load from the templates folder
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_filename)  # Our Jinja2 template file

    rendered_output = template.render(data=data)
    output_path = Path(filename)
    output_path.write_text(rendered_output, encoding="utf-8")


def read_tasks(filename):
    task_re = re.compile('\[(?P<tick>.)\] (Status: .*) (Project: .*) .* [a-z0-9\-]+')
    task_re = re.compile('\[(?P<tick>.)\] \(Status: (?P<status>[^\)]*)\) \(Project: (?P<project>[^\)]*)\) .* (?P<uuid>[a-z0-9\-]+)')
    #[ ] (Status: pending) (Project: ) Use and return Fincham's tools 80f6d55e-bf05-44b2-9bff-15f401ea4208


    # Scan tasks
    md = MarkdownIt()
    heading_filter = ["Open Tasks"]
    # TODO: Create file if it does not exist, don't just crash
    tokens = md.parse(Path(filename).read_text())
    current_heading = None
    inside_list_item = False
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open":
            current_heading = tokens[i + 1].content  # heading text is always next token
        if tok.type == "list_item_open":
            inside_list_item = True
        if tok.type == "list_item_close":
            inside_list_item = False
        if not heading_filter or current_heading not in heading_filter:
            continue
        if inside_list_item and tok.type == "inline":
            #print(current_heading)
            match = task_re.match(tok.content)
            if match:
                # print(match.group('tick'))
                if match.group('tick') != ' ':
                    mark_task_complete(match.group('uuid'))
                # print(match.group('status'))
                # print(match.groups())
            # print(tok.content)
            # print(tok.type)
            # print(tok)


def read_new_tasks(filename, tasks):
    # Scan tasks
    md = MarkdownIt()
    tokens = md.parse(Path(filename).read_text())
    current_heading = None
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open":
            current_heading = tokens[i + 1].content  # heading text is always next token
        if current_heading == "Create Task":
            print(current_heading)
            print(tok.type)
            print(tok)


def main():
    config.read(Path(config_filename))
    # print(config['DEFAULT']['output_file'])

    print("Getting tasks from taskwarrior")

    # read_new_tasks(config["DEFAULT"]["new_tasks_file"], tasks)
    # sys.exit()

    # Parse task list
    print("Reading Obsidian Task List")
    read_tasks(config["DEFAULT"]["output_file"])

    tasks = get_tw_tasks()

    # When detecting new tasks, wait for list of new tasks to have not changed for some period of time
    # to prevent us from creating a task that has only been half-written.

    print("Writing Obsidian Task List to " + config["DEFAULT"]["output_file"])
    write_markdown(config["DEFAULT"]["output_file"], "task-list.j2", tasks)


if __name__ == "__main__":
    main()
