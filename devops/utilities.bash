#########################################
# BASH UTILITIES FOR DOCKER
# Source this file in your .bash_profile
#########################################

alias d='docker'
alias dl='docker ps -l -q'

#Stops and remove all containers
docker_cleanup(){
	printf "Stoping all docker containers\n"
	docker stop $(docker ps -a -q);
	printf "Removing all docker containers\n"
	docker rm $(docker ps -a -q);
}

#Open the bash on a specific container
docker_enter_container(){
	LAST=false
	ERROR=false

	local OPTIND o a
	while getopts ":lL" opt; do
	  case "$opt" in
	    l|L)
	      LAST=true
	      ;;
	    \?)
	      ERROR=true
	      ;;
	  esac
	done

	if [ $ERROR == true ]
		then
		printf "Incorrect option\n"
	elif [ $LAST == true ]
		then
		docker exec -it $(dl) /bin/bash
	elif [ $1 ]
		then
		printf "Entering $1 container\n"
		docker exec -it $1 /bin/bash
	else
    	printf "You must pass the container id\n"
	fi
}

docker_logs(){
	docker-compose logs; while [ $? -ne 0 ]; do docker-compose logs; done;
}
