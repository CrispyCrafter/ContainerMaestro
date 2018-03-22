# ContainerMaestro

A streamlined dev pipeline for local container debugging and google cloud deployment.

```
usage: ./maestro.sh [OPTIONS]
        -h --help       - Display help files
        -i --init       - Initialize environment variables
        -l --local      - Spool up local mysql-docker image with docker compose
        -b --bash       - SSH into local Docker image instance
        -c --create     - Create compute instance on gcloud
        -p --push       - Build updated docker image and push to gcloud
        -k --keys       - Create DB authentication keys
        -d --deploy     - Deploy updated YAML file
        -s --shell      - SSH into google cloud pod/deployment
        -t --terminate  - Terminate all instances
```
---
## Requirements:
Python 3.x.x

[Google cloud SDK](https://cloud.google.com/sdk/)

[Docker](https://www.docker.com/get-docker)

[Kubernetes command-line tool](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

*Platform specific requirements*
- MAC-OSX
_get-opt_ : ```brew install gnu-getopt```

## Local development:
For local development run:
```
./maestro.sh --local
```
This will create:

 | Instance      |      Type     |  Address                      |
 | ------------- |:-------------:| -----------------------------:|
 | MySQL         | server        | 127.0.0.1:3306                |
 | NGINX         | server/debug  | 127.0.0.1:8090/nginx_status   |
 | phpmyadmin    | server        | 127.0.0.1:8082                |
 | Django        | app           | 127.0.0.1:80                  |
 | Django        | app           | 127.0.0.1:443                 |


 ## Cloud deployment:

 For cloud deployment run:
 ```
 ./maestro.sh -icpkd
 ```
 This will:
 1) Create cloud compute instance (See maestro.sh for fine tuning )
 2) Build and push local Docker image to a Google cloud bucket
 3) Create Database authentication keys
 4) Deploy test Django app to Kubernetes cluster

 Be sure to also [expose](https://console.cloud.google.com/kubernetes/discovery) the deployment to a desired port on the kubernetes engine in google cloud console  

### Usage:
For Google cloud functionality complete the following set of guidelines, making note of the listed environment variables.

1) Setting up Kubernetes with Google cloud:

⋅⋅⋅ https://cloud.google.com/kubernetes-engine/docs/quickstart

⋅⋅⋅ PROJECT_ID

⋅⋅⋅ COMPUTE_ZONE

⋅⋅⋅ CLUSTER_NAME

2) Setting up MySQL with Docker:

⋅⋅⋅ https://cloud.google.com/sql/docs/mysql/connect-kubernetes-engine

⋅⋅⋅ Be sure to make note of the following environment variables:

⋅⋅⋅ PROXY_KEY_FILE_PATH

⋅⋅⋅ INSTANCE_CONNECTION_NAME

⋅⋅⋅ DB_PASSWORD

3) Create a database on Cloud MySQL and note the database name as:

⋅⋅⋅DB_NAME

Initialize global environment variables:
```
./maestro.sh --init
```

This will create the following files:
```
env
├── dockerENVs
└── gcloudENVs

k8s
└── kubectl-deployment.yml
```
When prompted insert environment variables detailed in A
