import os

enVARS = {
        'PROJECT_DIR'  :  os.environ['PROJECT_DIR'],
        'PROJECT_ID'   :  os.environ['PROJECT_ID'],
        'COMPUTE_ZONE' :  os.environ['COMPUTE_ZONE'],
        'CLUSTER_NAME' :  os.environ['CLUSTER_NAME'],
        'APP_NAME'     :  os.environ['APP_NAME'],
        'APP_VERSION'  :  os.environ['APP_VERSION'],
        'DB_PASSWORD'  :  os.environ['DB_PASSWORD'],
        'DB_NAME'      :  os.environ['DB_NAME'],
        'INSTANCE_CONNECTION_NAME' : os.environ['INSTANCE_CONNECTION_NAME'],
        'PROXY_KEY_FILE_PATH' :  os.path.join(os.environ['PROJECT_DIR']+'/k8s/',
                                              os.environ['PROXY_KEY_FILE_PATH'].split("/")[-1]),
        }

def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def writeSecretENV(**kwargs):
    template ="""#!/bin/bash
#Set current project directory
export PROJECT_DIR={PROJECT_DIR}

# Set compute instance details - see cloudTools --create
export PROJECT_ID={PROJECT_ID}
export COMPUTE_ZONE={COMPUTE_ZONE}
export CLUSTER_NAME={CLUSTER_NAME}

# Specify application info
export APP_NAME={APP_NAME}
export APP_VERSION={APP_VERSION}
export IMAGE_NAME=gcr.io/{PROJECT_ID}/{APP_NAME}:{APP_VERSION}
export IMAGE_NGINX=gcr.io/{PROJECT_ID}/nginx:{APP_VERSION}
export DEPLOYMENT={APP_NAME}deployment

# Specify database info
export PROXY_KEY_FILE_PATH={PROXY_KEY_FILE_PATH}
export DB_PASSWORD={DB_PASSWORD}
export INSTANCE_CONNECTION_NAME={INSTANCE_CONNECTION_NAME}
export DB_NAME={DB_NAME}"""

    if not os.path.exists('env/gloudENVs'):
        touch('env/gcloudENVs')

    with open('env/gcloudENVs', 'w') as yfile:
        yfile.write(template.format(**kwargs))

def populateENV():
    envTest = input('Update app version (y/N) ? \n')
    if envTest in ('y','Y','Yes','yes'):
        prompt = input('Populate all environment variables ? (y/N): \n')
        if prompt in ('y','Y','Yes','yes'):
            enVARS['PROJECT_DIR']  = os.getcwd()
            enVARS['PROJECT_ID']   = input('Enter the current project ID on google cloud: \n')
            enVARS['COMPUTE_ZONE'] = input('Enter compute zone: \n')
            enVARS['CLUSTER_NAME'] = input('Enter cluster name: \n')
            enVARS['APP_NAME']     = input('Enter app name: \n')
            enVARS['APP_VERSION']  = input('Enter app version (vX.X) \n')
            print('From google cloud setup guide 1) (mysql-kubernetes)')
            print('Assuming *.json is stored in env/*.json')
            enVARS['PROXY_KEY_FILE_PATH'] = input('Enter proxy key filepath generated from gcloud setup guide 1: \n')
            enVARS['DB_PASSWORD'] = input('Enter DB password created from gcloud setup guide 1: \n')
            enVARS['INSTANCE_CONNECTION_NAME'] = input('Enter DB instance connection name generated from gcloud setup guide 1 \n')
            enVARS['DB_NAME'] = input('Specify database name: \n')
            # Write ENVs to file
            writeSecretENV(**enVARS)

        elif prompt in ('n','N','No','no'):
            print('Changing app version:')
            print('Current app version is {}'.format(os.environ['APP_VERSION']))
            enVARS['APP_VERSION']  = input('Enter app version (vX.X) \n')
            enVARS['PROJECT_DIR']  = os.getcwd()
            # Write ENVs to file
            writeSecretENV(**enVARS)

    elif envTest in ('n','N','No','no'):
        print("Keeping app version {}".format(os.environ['APP_VERSION']))
        enVARS['PROJECT_DIR']  = os.getcwd()
        writeSecretENV(**enVARS)
    else:
        print("Invalid option selected try again")
        populateENV()

def writeDockerComposeENV(**kwargs):
    template ="""#!/bin/bash
MYSQL_ROOT_PASSWORD={DB_PASSWORD}
MYSQL_USER=proxyuser
MYSQL_PASSWORD={DB_PASSWORD}
MYSQL_DATABASE={DB_NAME}
DB_PASSWORD={DB_PASSWORD}
DB_USER=proxyuser
DB_NAME={DB_NAME}
DB_HOST=db """

    if not os.path.exists('env/dockerENVs'):
        touch('env/dockerENVs')

    with open('env/dockerENVs', 'w') as yfile:
        yfile.write(template.format(**kwargs))


# initialise environment variables
populateENV()
writeDockerComposeENV(DB_PASSWORD=os.environ['DB_PASSWORD'],DB_NAME=os.environ['DB_NAME'])
