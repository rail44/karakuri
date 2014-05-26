import argparse
from .project import Project

def main():
    parser = argparse.ArgumentParser(description='Exec project defined given image')
    parser.add_argument('image_name', metavar='image', type=str, help='a name of image')
    args = parser.parse_args()

    Project(args.image_name).up()
