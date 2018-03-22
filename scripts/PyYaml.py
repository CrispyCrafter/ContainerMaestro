import os
name  = os.environ["APP_NAME"]+"deployment"
app_name = os.environ["APP_NAME"]
#image = os.environ["IMAGE_NAME"].split(":")[0] + ":latest"
image = os.environ["IMAGE_NAME"]
cdir  = os.environ["PROJECT_DIR"]
dbinstance = os.environ["INSTANCE_CONNECTION_NAME"]

print("Generating YAML file with parameters:")
print("name : {}".format(name))
print("image: {}".format(image))
print("dir  : {}".format(cdir))

def writeScrapyYAML(cdir,**kwargs):
    template ="""apiVersion: v1
kind: Pod
metadata:
  name: {name}
  labels:
    app: {name}
spec:
  containers:
  - name: {app_name}
    image: {image}
    imagePullPolicy: Always
    env:
    - name: DB_HOST
      value: 127.0.0.1
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: cloudsql-db-credentials
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: cloudsql-db-credentials
          key: password"""

    with open('k8s/single_pod.yaml'.format(cdir), 'w') as yfile:
        print("Writing file")
        yfile.write(template.format(**kwargs))

def writeDeploymentYAML(cdir,**kwargs):
    template ="""apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {name}
  labels:
    app: {name}
spec:
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
        - name: {app_name}
          image: {image}
          imagePullPolicy: Always
          env:
            - name: DB_HOST
              value: 127.0.0.1
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: cloudsql-db-credentials
                  key: username
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: cloudsql-db-credentials
                  key: password
        - name: cloudsql-proxy
          image: gcr.io/cloudsql-docker/gce-proxy:1.11
          command: ["/cloud_sql_proxy",
                    "-instances={dbinstance}=tcp:3306",
                    "-credential_file=/secrets/cloudsql/credentials.json"]
          volumeMounts:
            - name: cloudsql-instance-credentials
              mountPath: /secrets/cloudsql
              readOnly: false
        # [END proxy_container]
      # [START volumes]
      volumes:
        - name: cloudsql-instance-credentials
          secret:
            secretName: cloudsql-instance-credentials
        - name: cloudsql
          emptyDir:"""

    with open('k8s/kubectl-deployment.yaml', 'w') as yfile:
        yfile.write(template.format(**kwargs))

# usage:
#writeScrapyYAML(cdir,app_name=app_name,image=image,name=name)
writeDeploymentYAML(cdir,app_name=app_name,image=image,name=name,dbinstance=dbinstance)
