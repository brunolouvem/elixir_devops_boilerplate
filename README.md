# Elixir Devops Boilerplate

This project is a guide for beginning elixir developers, starting a project, with docker


1) First usage
---------------------------

### Export enviroment variables on env folder
```bash
$ ./env/local.sh
```

### Generate docker files and required enviroment variables for both local and production environments
```bash
$ ./devops/build_files.py
```

### (Optional) Add bash utilities to your .bash_profile
```bash
source <project_path>/devops/docker/utilities.bash
```

2) Running/Building image
---------------------------
```bash
$ docker-compose up -d
```

3) Docker's bash utilities
---------------------------
```bash
# Stop and remove all docker active containers
$ docker_cleanup

# Enter a running container without needing password or keys
$ docker_enter_container [<container-id> | -L ]
Args:
	<container-id> -> Enter a given running container
	-L -> Enter the last running container


# See logs for all running containers orchestrated by docker-compose
$ docker_logs

```

Dependencies
---------------------------
 * Docker
 * docker-compose
 * Python 2/3
