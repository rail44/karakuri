import os
import sys
import yaml
import tarfile
import re
from io import BytesIO
from uuid import uuid4
from string import Template

from fig.project import Project as FigProject
from fig.container import Container
from fig.packages import docker
from fig.packages.docker.errors import APIError

class Project:
    def __init__(self, image_name):
        self.client = docker.Client(
            base_url=os.getenv('DOCKER_HOST', 'unix://var/run/docker.sock'),
            version='1.12'
        )
        m = re.search(':(.*)', image_name)
        self.tag = m.group(1) if m else 'latest'
        inspect = self.client.inspect_image(image_name)
        self.image_name = inspect['Id']

    def do(self, task, args):
        config = self.get_fig_config(task)
        if args:
            config['main']['command'] += ' {0}'.format(' '.join(args))
        project = FigProject.from_config(self.image_name, config, self.client)
        for container in project.up():
            if container.name == '{0}_main_1'.format(self.image_name):
                for chunk in container.attach(stderr=True, stdout=True, stream=True):
                    sys.stdout.write(chunk)
                inspect = container.inspect()
                code = inspect['State']['ExitCode']
                break
        config.pop('main', None)
        if config:
            project.stop(service_names=config.keys())
        return code

    def rm(self):
        config = self.get_fig_config('')
        project = FigProject.from_config(self.image_name, config, self.client)
        project.remove_stopped(v=True)

    def tasks(self):
        config = self.get_config()
        default = config.get('default', '')
        tasks = config['tasks']
        try:
            tasks['{0}(default)'.format(default)] = tasks.pop(default)
        except KeyError:
            pass
        return tasks

    def get_config(self):
        tmp_container = Container.create(self.client, image=self.image_name, command='true')
        try:
            res = self.client.copy(tmp_container.name, '/karakuri.yml')
        except APIError:
            work_dir = tmp_container.inspect()['Config']['WorkingDir']
            res = self.client.copy(tmp_container.name, '{0}/karakuri.yml'.format(work_dir))
        tmp_container.remove()
        io = BytesIO()
        io.write(res.data)
        io.seek(0)
        tar = tarfile.open(mode='r:', fileobj=io)
        config_str = tar.extractfile('karakuri.yml').read()
        config_str = Template(config_str).substitute(TAG=self.tag)
        return yaml.load(config_str)

    def get_fig_config(self, task):
        config = self.get_config()

        default = config.pop('default', '')
        tasks = config.pop('tasks', [])
        fig_config = config.pop('services', {})
        fig_config['main'] = config
        fig_config['main']['image'] = self.image_name

        if task == '':
            task = default
        if task in tasks:
            fig_config['main']['command'] = tasks[task]
        else:
            fig_config['main']['command'] = True
        return fig_config
