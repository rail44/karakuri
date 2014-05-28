import sys
import argparse
from .project import Project

def main():
    parser = argparse.ArgumentParser(description='Exec project defined given image')
    parser.add_argument('image_name', metavar='image', type=str, help='a name of image')
    parser.add_argument('task', metavar='task', type=str, nargs='?', default='', help='a task to exec')
    args = parser.parse_args()

    code = Project(args.image_name).up(args.task)
    sys.exit(code)
