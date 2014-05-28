import os
import sys
import yaml

from uuid import uuid4
from fig.project import Project as FigProject
from fig.packages import docker

class Project:
    def __init__(self, image_name):
        self.name = str(uuid4()).replace('-', '')
        self.image_name = image_name
        self.main_container_name = '{}_main_1'.format(self.name)
        self.client = docker.Client(
            base_url=os.getenv('DOCKER_1_PORT', 'unix://var/run/docker.sock'),
            version='1.9',
            timeout=10
        )

    def up(self, task):
        self.create_main_container()
        config = self.get_config()
        if not config['main'].has_key('default'):
            raise RuntimeError
        default = config['main'].pop('default', '')
        tasks = config['main'].pop('tasks', [])
        if task == '':
            task = default
        for t in tasks:
            if t == task:
                config['main']['command'] = tasks[t]
        project = FigProject.from_config(self.name, config, self.client)
        for container in project.up():
            if container.name == self.main_container_name:
                for chunk in container.logs(stream=True):
                    sys.stdout.write(chunk)
                inspect = self.client.inspect_container(container.id)
                code = inspect['State']['ExitCode']
                break
        project.remove_stopped()
        return code

    def create_main_container(self):
        self.client.create_container(self.image_name, name=self.main_container_name)

    def get_config(self):
        config_list = self.client.copy(self.main_container_name, '/karakuri.yml').read(list).split('\0')
        config_list = filter(None, config_list)
        config = yaml.load(config_list[-1])
        config['main']['image'] = self.image_name
        return config
