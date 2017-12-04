#!/usr/bin/env python
import os
import socket

from datetime import datetime
from os.path import basename, dirname, realpath, join, abspath

__LOCAL__ = 'local'
__PRODUCTION__ = 'production'

PAINT_RED='\033[00;31m'
PAINT_GREEN='\033[01;32m'
PAINT_PURPLE='\033[00;35m'
PAINT_CYAN='\033[01;36m'
PAINT_YELLOW='\033[01;33m'
END_COLOR="\033[00m"
LINE_BREAK='\n'

"""
Path to base folders (devops and project's root)
"""
DEVOPS_FOLDER_PATH = dirname(realpath(__file__))
PROJECT_ROOT_PATH = abspath(join(DEVOPS_FOLDER_PATH, os.pardir))
devops_directory = lambda dir: join(DEVOPS_FOLDER_PATH, dir)

"""
Path to folder containing base (template) files to be generated
"""
BASE_FILES_PATH = devops_directory('base_files')
DOCKER_COMPOSE_BASE_FILE = join(BASE_FILES_PATH, 'docker-compose.base')
DOCKERFILE_BASE_FILE = join(BASE_FILES_PATH, 'Dockerfile.base')
DOCKERFILE_PRODUCTION_BASE_FILE = join(BASE_FILES_PATH, 'Dockerfile.production.base')
VERSION_FILE = join(DEVOPS_FOLDER_PATH, 'version.txt')

"""
Path to subfolders inside devops folder to hold config files
based on the the environment name
"""
DEVOPS_LOCAL_PATH = devops_directory(__LOCAL__)
DEVOPS_PRODUCTION_PATH = devops_directory(__PRODUCTION__)

"""
Path to files containing environment variable in the following format
export VAR_NAME=VAR_VALUE
"""
PROD_ENV_VARIABLES = join(PROJECT_ROOT_PATH, 'env', 'production.sh')
LOCAL_ENV_VARIABLES = join(PROJECT_ROOT_PATH, 'env', 'local.sh')
"""
"""
FILENAME_DOCKER_COMPOSE = 'docker-compose.yml'
FILENAME_DOCKERFILE = 'Dockerfile'
FILENAME_DOCKER_ENV_VAR = 'variables.env'

def main():
    print(LINE_BREAK)
    generate_files_local_env()
    generate_files_production_env()
    print(LINE_BREAK)

def generate_files_local_env():

    generate_environment_variables_file(__LOCAL__)
    generate_docker_compose_file(__LOCAL__)
    generate_dockerfile(__LOCAL__)

def generate_files_production_env():

    generate_environment_variables_file(__PRODUCTION__)
    generate_dockerfile(__PRODUCTION__)

def generate_environment_variables_file(env):

    fp_new_file = create_file(env, FILENAME_DOCKER_ENV_VAR)

    if env == __PRODUCTION__:
        variables_file = PROD_ENV_VARIABLES
    else:
        variables_file = LOCAL_ENV_VARIABLES

    with open(variables_file, 'r') as file:
        export = 'export '
        comment = '#'
        ignore_keys = ['REDIS_', 'DB_']

        for line in file:
            if env == __LOCAL__:
                if not is_valid_line(ignore_keys, line):
                    continue

            if line.startswith(export):
                fp_new_file.write(line.replace(export, ''))

            elif line.startswith(comment):
                continue

    fp_new_file.close()
    print(build_file_generation_message(env, FILENAME_DOCKER_ENV_VAR))

def generate_docker_compose_file(env):

    fp_new_file = create_file(env, FILENAME_DOCKER_COMPOSE)

    with open(DOCKER_COMPOSE_BASE_FILE, 'r') as file:

        key_hostname = '<#HOSTNAME#>'
        key_project_path = '<#PROJECT-PATH#>'
        key_version = '<#VERSION#>'

        for line in file:
            new_line = line

            if key_hostname in line:
                new_line = line.replace(key_hostname, gen_hostname())
            if key_project_path in line:
                new_line = line.replace(key_project_path, PROJECT_ROOT_PATH)
            if key_version in line:
                new_line = line.replace(key_version, get_version())

            fp_new_file.write(new_line)

    fp_new_file.close()
    print(build_file_generation_message(env, FILENAME_DOCKER_COMPOSE))

def generate_dockerfile(env):

    fp_new_file = create_file(env, FILENAME_DOCKERFILE)

    if env == __PRODUCTION__:
        destination = DEVOPS_PRODUCTION_PATH
        dockerfile = DOCKERFILE_PRODUCTION_BASE_FILE
        variables_file = join(destination, FILENAME_DOCKER_ENV_VAR)

    else:
        destination = DEVOPS_LOCAL_PATH
        dockerfile = DOCKERFILE_BASE_FILE
        variables_file = join(destination, FILENAME_DOCKER_ENV_VAR)

    with open(dockerfile, 'r') as file:
        env_block = '<#ENV#>'
        key_version = '<#VERSION#>'
        ignore_keys = ['REDIS_', 'DB_', 'DATABASE_URL']

        for line in file:
            new_line = line

            if key_version in line:
                new_line = line.replace(key_version, get_version())

            if line.startswith(env_block):
                docker_formated_variables = []
                with open(variables_file, 'r') as variables:
                    for variable in variables:
                        if not is_valid_line(ignore_keys, variable):
                            continue
                        docker_formated_variables.append('ENV ' + variable)
                new_line = ''.join(docker_formated_variables)

            fp_new_file.write(new_line)

    fp_new_file.close()
    print(build_file_generation_message(env, FILENAME_DOCKERFILE))

    #Remove variables file since it's not necessary in production envs
    if env == __PRODUCTION__:
        os.remove(variables_file)

def get_version():
    with open(VERSION_FILE, 'r') as file:
        first_line = file.readline()
        return first_line.strip()

def is_valid_line(invalidation_list, line):
    """
    Check string validity against a list of invalid substring
    """
    for invalid_key in invalidation_list:
            if invalid_key in line:
                return False
    return True


def create_file(env, filename):
    """
    Create and return new file based on destination and filename
    """
    if env == __PRODUCTION__:
        destination = DEVOPS_PRODUCTION_PATH

    else:
        destination = DEVOPS_LOCAL_PATH

    new_file = join(destination, filename)
    return open(new_file, 'w')

def build_file_generation_message(env, filename):
    """
    Format message to be used when file a new file is generated.
    """
    return (
        c(PAINT_PURPLE, '---------------------------') +
        LINE_BREAK +
        c(PAINT_CYAN, 'Environment: {} '.format(env)) +
        LINE_BREAK +
        c(PAINT_YELLOW, '{} '.format(filename)) +
        c(PAINT_GREEN, 'was generated successfully')
    )



def gen_hostname():
    """
    Generate random compliant hostname based on user's own hostname
    to avoid hostnames's clash in development environment.
    """
    return '{}-{}'.format(
        datetime.now().microsecond, socket.gethostname())

def c(color, message):

    return color + message + END_COLOR

if __name__ == '__main__':
    main()
