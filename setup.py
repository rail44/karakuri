import os
from pip.req import parse_requirements
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = parse_requirements('./requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name = 'karakuri',
    version = '0.2.3',
    author = 'Satoshi Amemiya',
    author_email = 'satoshi_amemiya@voyagegroup.com',
    description = 'Task management tool for docker image',
    license = 'BSD',
    keywords = 'docker',
    url = 'http://github.com/rail44/karakuri',
    packages=['karakuri'],
    long_description=read('README.md'),
    install_requires=reqs,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Topic :: Utilities',
      'License :: OSI Approved :: BSD License',
    ],
    entry_points="""
    [console_scripts]
    karakuri=karakuri.run:main
    """
)
