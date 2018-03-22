import os
enVARS = {
    "name"        : os.environ["APP_NAME"]+"deployment",
    "app_name"    : os.environ["APP_NAME"],
    "app_image"   : os.environ["IMAGE_NAME"],
    "nginx_image" : os.environ["IMAGE_NGINX"],
    "cdir"        : os.environ["PROJECT_DIR"],
    "dbinstance"  : os.environ["INSTANCE_CONNECTION_NAME"],
    "deployment"  : os.environ["DEPLOYMENT"]
}

print("Generating YAML file with parameters:")
print("name : {}".format(enVARS["name"]))
print("image: {}".format(enVARS["app_image"]))
print("dir  : {}".format(enVARS["cdir"]))

def writeServicesYAML(**kwargs):
    template ="""apiVersion: "v1"
kind: "Service"
metadata:
    name: "{deployment}-service"
    namespace: "default"
    labels:
        app: "{deployment}"
spec:
    ports:
    - name: "443-to-443-tcp"
        protocol: "TCP"
        port: 443
    - name: "80-to-80-tcp"
        protocol: "TCP"
        port: 80
    selector:
        app: "{deployment}"
    type: "LoadBalancer"
    loadBalancerIP: """

    with open('k8s/main-services.yml', 'w') as yfile:
        print("Writing file")
        yfile.write(template.format(**kwargs))

def writeDeploymentYAML(**kwargs):
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
          image: {app_image}
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
          ports:
            - containerPort: 8081
        - name: cloudsql-proxy
          image: gcr.io/cloudsql-docker/gce-proxy:1.11
          command: ["/cloud_sql_proxy",
                    "-instances={dbinstance}=tcp:3306",
                    "-credential_file=/secrets/cloudsql/credentials.json"]
          volumeMounts:
            - name: cloudsql-instance-credentials
              mountPath: /secrets/cloudsql
              readOnly: false
        - name: nginx
          image: {nginx_image}
          imagePullPolicy: Always
          ports:
            - containerPort: 80
            - containerPort: 443
            - containerPort: 8090
        # [END proxy_container]
      # [START volumes]
      volumes:
        - name: cloudsql-instance-credentials
          secret:
            secretName: cloudsql-instance-credentials
        - name: cloudsql
          emptyDir:"""

    with open('k8s/main-deployment.yml', 'w') as yfile:
        yfile.write(template.format(**kwargs))

writeServicesYAML(**enVARS)
writeDeploymentYAML(**enVARS)
