from __future__ import print_function
import sys
import argparse
from .project import Project

def main():
    parser = argparse.ArgumentParser(description='Exec project defined given image')
    parser.add_argument('image_name', metavar='image', type=str, help='a name of image')
    sub_parsers = parser.add_subparsers(title='command', metavar='command')

    do_parser = sub_parsers.add_parser('do', help='exec task')
    do_parser.add_argument('task', metavar='task', type=str, nargs='?', default='', help='a task to exec')
    do_parser.set_defaults(func=do)

    do_parser = sub_parsers.add_parser('rm', help='remove stopped containers')
    do_parser.set_defaults(func=rm)

    tasks_parser = sub_parsers.add_parser('tasks', help='show tasks')
    tasks_parser.set_defaults(func=tasks)

    args = parser.parse_args()
    args.func(args)

def do(args):
    code = Project(args.image_name).do(args.task)
    sys.exit(code)

def rm(args):
    Project(args.image_name).rm()

def tasks(args):
    tasks = Project(args.image_name).tasks()
    print('[task]'.ljust(32), '[command]')
    for task, cmd in tasks.items():
        print(task.ljust(32), cmd)
