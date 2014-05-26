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

Create `karakuri.yml' for your product.

example:

    main:
      command: bundle exec rspec
      links:
        - db
    db:
      image: orchardup/postgresql
      ports:
        - "5432"

Base systax is equivalent [fig.yml](http://orchardup.github.io/fig/yml.html), but `image` and `build` must not spcify.  
You should assign just one Service named `main`.

Environment variables are avilable for linked containers.  
It is able to use same as [fig's](http://orchardup.github.io/fig/env.html).  
For above example, you can use `$DB_1_PORT` in your app's database config.

At last, add this line your Dockerfile.

    ADD ./karakuri.yml /karakuri.yml

## Usage

    docker build -t <image_name> .
    karakuri <image_name>

**Karakuri** is going to support management of building image.
