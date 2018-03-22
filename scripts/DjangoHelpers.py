import os
import subprocess
import logging
from tempfile import mkstemp
from shutil import move
import re


dir = os.getcwd()
os.environ.get('pod/gloudENVs')

def runBash(commands):
    if type(commands) is not list:
        commands = [commands]
        runBash(commands)
    else:
        for command in commands:
            process =  subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            logging.debug(output)
            if error is not None:
                logging.error(error)

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with os.fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(
                                re.sub(r'^.*{}.*$'.format(pattern),
                                '{}'.format(subst),
                                line)
                              )
    #Remove original file
    os.remove(file_path)
    #Move new file
    move(abs_path, file_path)


createBucket = input("Create google cloud static bucket (y/N) \n")

if createBucket in ['y','Y','Yes','yes']:

    createComms = [
    "gsutil mb gs://{}".format(os.environ['DEPLOYMENT']),
    "gsutil defacl set public-read gs://{}".format(os.environ['DEPLOYMENT']),
                  ]
    runBash(createComms)

elif createBucket in ['n','N','No','no']:
    print('Assuming bucket static bucket already exists')

print('Pushing staticfiles to cloud bucket http://storage.googleapis.com/{}/static/'.format(os.environ['DEPLOYMENT']))

pushComms = [
"python3 {} collectstatic --noinput".format(
    os.path.join(os.environ['PROJECT_DIR'],'code/django_app/manage.py') ),
"gsutil rsync -R -m -o {}/code/django_app/static/ gs://{}/static".format(
    os.environ['PROJECT_DIR'],
    os.environ['DEPLOYMENT']
    ),
]

replace(
'{}'.format(os.path.join(os.environ['PROJECT_DIR'],'code/django_app/django_app/settings.py')),
'{}'.format('STATIC_URL = '),
'{} "http://storage.googleapis.com/{}/static/" '.format('STATIC_URL =' ,os.environ['DEPLOYMENT'])
    )


runBash(pushComms)
