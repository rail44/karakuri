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

    def up(self):
        self.create_main_container()
        service = FigProject.from_config(self.name, self.get_config(), self.client).get_service('main')
        service.recreate_containers()
        service.start()
        for chunk in self.client.logs(self.main_container_name, stream=True):
            sys.stdout.write(chunk)
        service.remove_stopped()

    def create_main_container(self):
        self.client.create_container(self.image_name, name=self.main_container_name)

    def get_config(self):
        config_list = self.client.copy(self.main_container_name, '/karakuri.yml').read(list).split('\0')
        config_list = filter(None, config_list)
        config = yaml.load(config_list[-1])
        config['main']['image'] = self.image_name
        return config
