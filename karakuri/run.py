#!/usr/bin/env python
import os
import sys
import argparse
import yaml

from uuid import uuid4
from fig.packages import docker
from fig.project import Project

def main():
  c = docker.Client(
      base_url=os.getenv('DOCKER_1_PORT', 'unix://var/run/docker.sock'),
      version='1.9',
      timeout=10
  )

  work_name = str(uuid4()).replace('-', '')
  parser = argparse.ArgumentParser(description='Exec project defined given image')
  parser.add_argument('image_name', metavar='image', type=str, help='a name of image')
  args = parser.parse_args()
  image_name = args.image_name

  container_name = '{}_main_1'.format(work_name)
  c.create_container(image_name, name=container_name)
  config_list = c.copy(container_name, '/karakuri.yml').read(list).split('\0')
  config_list = filter(None, config_list)
  config = yaml.load(config_list[-1])
  config['main']['image'] = image_name

  service = Project.from_config(work_name, config, c).get_service('main')
  service.recreate_containers()
  service.start()
  for chunk in c.logs(container_name, stream=True):
      sys.stdout.write(chunk)
