# Karakuri

Task manager for docker image

## Requirements

* Python2
* pip
* Docker(either local or remote)

## Installation

    pip install karakuri

or

    pip install git+https://github.com/rail44/karakuri.git

## Config

Create `karakuri.yml` for your product.

example:

    tasks:
      start: bundle exec rake start
      test: bundle exec rspec
    default: start
    links:
      - db
      - cache
    services:
      db:
        image: orchardup/postgresql
        ports:
          - "5432"
      cache:
        image: tutum/memcached
        ports:
          - "11211"
        

Base systax is equivalent [fig.yml](http://orchardup.github.io/fig/yml.html).

Environment variables are avilable for linked containers.  
It is able to be used same as [fig's](http://orchardup.github.io/fig/env.html).  
For above example, you can use `$DB_1_PORT` in your app's database config.

**Karakuri** will try to find `karakuri.yml` from root(`/`) or `WORKDIR`.  
You must add it to either.

## Usage

    docker build -t <image_name> .
    karakuri <image_name> <command>

If `$DOCKER_HOST` is defined, **Karakuri** will set it for Docker daemon.  
For example, you can be able to run test with

    karakuri <image_name> do test
