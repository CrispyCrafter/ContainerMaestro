#!/bin/bash
# Container Maestro was developed to streamline the process of local code iteration
# and google cloud execution.

if [ ! -d env ]; then
  mkdir env
fi

probeENVs () {
  if [ ! -f env/gcloudENVs ] || [ ! -f env/dockerENVs ]; then
      echo "Google cloud environment variables not not found!"
      echo "Please refer to README for details regarding each environment variables"
      source env/gcloudENVs;
      python3 scripts/PySecrets.py;
      python3 scripts/PyYaml.py;
      exit 0
  fi
}

init () {
  probeENVs;
  source env/gcloudENVs;
  python3 scripts/PySecrets.py;
  python3 scripts/PyYaml.py;
  gcloud config set project $PROJECT_ID;
  gcloud config set compute/zone $COMPUTE_ZONE;
}

update () {
  source env/gcloudENVs;
  python3 scripts/PySecrets.py;
  python3 scripts/PyYaml.py;
  source env/gcloudENVs;
}

# Call getopt to validate the provided input.
OPTS=`getopt -o hilbcpkdst --long help,init,local,bash,create,push,keys,deploy,shell,terminate -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

eval set -- "$OPTS"

show_help () {
cat << USAGE
usage: ./maestro.sh [OPTIONS]
        -h --help       - Display help files
        -i --init       - Initialize environment variables
        -l --local      - Spool up local mysql-docker image with docker compose
        -b --bash       -  SSH into local Docker image instance
        -c --create     - Create compute instance on gcloud
        -p --push       - Build updated docker image and push to gcloud
        -k --keys       - Create DB authentication keys
        -d --deploy     - Deploy updated YAML file
        -s --shell      - SSH into google cloud pod/deployment
        -t --terminate  - Terminate all instances
USAGE
exit 0
}

while true; do
  case "$1" in
	-h | --help )
		show_help;
		shift;
	;;
 	 -i | --init )
		init;
		shift;
	;;
	-l | local )
		update;
		docker-compose config;
		docker-compose build;
		docker-compose up -d;
		docker ps;
		PODLOCAL=$(docker ps | grep "_web_1" | awk '{print $1}');
    echo -e '\nPODLOCAL='${PODLOCAL} >> env/dockerENVs
		shift;
	;;
	-b | --bash )
    source env/dockerENVs
		docker exec -it -erm $PODLOCAL bash;
		shift;
	;;
	-c | --create )
		echo "Creating compute instances";
		gcloud container clusters create $CLUSTER_NAME \
			--num-nodes=3 \
			--machine-type=g1-small \
			--zone=$COMPUTE_ZONE \
			--disk-size=10\
			--preemptible;
		shift
	;;
	-p | --push )
		update;
		echo "Building docker image" ;
		docker build -t ${IMAGE_NAME} . -f docker/django/Dockerfile;
		echo "Pushing docker image to cloud" ;
		gcloud docker -- push ${IMAGE_NAME} ;
		shift
	;;
	-k | --keys )
		echo "Creating image keys"
		kubectl create secret generic cloudsql-instance-credentials --from-file=credentials.json=${PROXY_KEY_FILE_PATH} ;
		kubectl create secret generic cloudsql-db-credentials --from-literal=username=proxyuser --from-literal=password=${PASSWORD} ;
		shift
	;;
	-d | --deploy )
		echo "Deploying Kubernetes configurations"
		echo "Updating build yaml"
		source env/gcloudENVs;
		python3 scripts/PyYaml.py;
		kubectl apply -f $PROJECT_DIR/k8s/kubectl-deployment.yaml;
		kubectl get pods;
		shift;
	;;
	-t | --terminate )
		echo "Terminating compute instance"
		gcloud container clusters delete $CLUSTER_NAME ;
		shift
	;;
	-s | --shell )
		kubectl get pods;
		source env/gcloudENVs;
	    	POD=$(kubectl get pods --include-uninitialized=false | grep ${DEPLOYMENT} | awk '{print $1}');
	    	echo "Attempting ssh connection to" $POD
	    	kubectl exec -it $POD -- /bin/bash;
	    	shift;
	;;
	-- ) shift; break ;;
	* ) break ;;
 	esac
done
