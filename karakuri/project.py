import os
import sys
import yaml
import tarfile
from io import BytesIO
from uuid import uuid4

from fig.project import Project as FigProject
from fig.container import Container
from fig.packages import docker
from fig.packages.docker.errors import APIError

class Project:
    def __init__(self, image_name):
        self.client = docker.Client(
            base_url=os.getenv('DOCKER_HOST', 'unix://var/run/docker.sock'),
            version='1.9',
            timeout=10
        )
        inspect = self.client.inspect_image(image_name)
        self.image_name = inspect['id']

    def do(self, task):
        config = self.get_fig_config(task)
        project = FigProject.from_config(self.image_name, config, self.client)
        for container in project.up():
            if container.name == '{0}_main_1'.format(self.image_name):
                for chunk in container.logs(stream=True):
                    sys.stdout.write(chunk)
                inspect = container.inspect()
                code = inspect['State']['ExitCode']
                break
        project.stop()
        return code

    def rm(self):
        config = self.get_fig_config('')
        project = FigProject.from_config(self.image_name, config, self.client)
        project.remove_stopped()

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
        tmp_container = Container.create(self.client, image=self.image_name, name=str(uuid4()).replace('-', ''))
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
        return yaml.load(tar.extractfile('karakuri.yml'))

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
