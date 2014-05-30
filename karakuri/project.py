import os
import sys
import yaml

from uuid import uuid4
from fig.project import Project as FigProject
from fig.container import Container
from fig.packages import docker
from fig.packages.docker.errors import APIError

class Project:
    def __init__(self, image_name):
        self.name = str(uuid4()).replace('-', '')
        self.image_name = image_name
        self.client = docker.Client(
            base_url=os.getenv('DOCKER_1_PORT', 'unix://var/run/docker.sock'),
            version='1.9',
            timeout=10
        )

    def do(self, task):
        self.create_main_container()
        config = self.get_fig_config(task)
        project = FigProject.from_config(self.name, config, self.client)
        for container in project.up():
            if container.name == self.main_container.name:
                for chunk in container.logs(stream=True):
                    sys.stdout.write(chunk)
                inspect = self.client.inspect_container(container.id)
                code = inspect['State']['ExitCode']
                break
        project.remove_stopped()
        return code

    def tasks(self):
        self.create_main_container()
        config = self.get_config()
        default = config.get('default', '')
        self.main_container.remove()
        tasks = config['tasks']
        tasks['{}(default)'.format(default)] = tasks.pop(default)
        return tasks

    def create_main_container(self):
        self.main_container = Container.create(self.client, image=self.image_name, name='{}_main_1'.format(self.name))

    def get_config(self):
        try:
            config_list = self.client.copy(self.main_container.name, '/karakuri.yml').read(list).split('\0')
        except APIError:
            work_dir = self.main_container.inspect()['Config']['WorkingDir']
            config_list = self.client.copy(self.main_container.name, '{}/karakuri.yml'.format(work_dir)).read(list).split('\0')

        config_list = filter(None, config_list)
        return yaml.load(config_list[-1])

    def get_fig_config(self, task):
        config = self.get_config()

        default = config.pop('default', '')
        tasks = config.pop('tasks', [])
        fig_config = config.pop('services', {})
        fig_config['main'] = config
        fig_config['main']['image'] = self.image_name

        if task == '':
            if default == '':
                raise RuntimeError
            task = default
        for t in tasks:
            if t == task:
                fig_config['main']['command'] = tasks[t]
        return fig_config
