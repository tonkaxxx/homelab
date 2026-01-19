## how to deploy all my homelab services

### how to deplpy longhorn

1. upd repo 
helm repo add longhorn https://charts.longhorn.io
helm repo update

2. make some additional tweaks for longhorn
```
mount --make-rshared /

apk update
apk add open-iscsi util-linux

rc-update add iscsid default
rc-service iscsid start

rc-service kubelet restart
```
4. apply chart
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace 

5. forward web ui
kubectl patch svc longhorn-frontend -n longhorn-system -p '{"spec":{"type":"NodePort","ports":[{"port":80,"targetPort":80,"nodePort":30000}]}}'

5.1 mb u will need this
kubectl -n longhorn-system patch svc longhorn-frontend \
  -p '{"spec":{"ports":[{"port":80,"targetPort":8000}]}}'

### prometheus metrics and alerts
#### if one of my nodes heats too much, i will get allert via tg messages 

1. install required packages
sudo apk add lm_sensors prometheus-node-exporter curl micro

2. add kernel module (for intel cpu)
sudo modprobe coretemp

3. create openrc service
sudo micro /etc/init.d/prometheus-node-exporter

```bash
#!/sbin/openrc-run
name="prometheus-node-exporter"
description="Prometheus Node Exporter"
command="/usr/bin/node_exporter"
command_args="--collector.hwmon --collector.thermal_zone"
command_user="nobody"
pidfile="/var/run/${name}.pid"

depend() {
    need net
}

start_pre() {
    checkpath -d -o nobody:nobody -m 755 "/var/lib/node_exporter"
}
```

4. make it executable
sudo chmod +x /etc/init.d/prometheus-node-exporter

5. enable service 
sudo rc-service prometheus-node-exporter start
sudo rc-update add prometheus-node-exporter default

6. test metrics (look for `node_hwmon_temp_celsius`)
curl http://localhost:9100/metrics | grep temp



### my python bot for lenses
#### this python bot counts 15 days, and texts to me, when i need to change my lenses

1. create namespace
kubectl create namespace bots

2. create secret with tg token
kubectl -n bots create secret generic lenses-bot-secret \
  --from-literal=TELEGRAM_BOT_TOKEN=UR_TOKEN

3. apply manifest
kubectl apply -f lenses.yaml -n bots


### homarr
#### homarr - dashboard for my cluster

1. install repo
```
helm repo add homarr-labs https://homarr-labs.github.io/charts/
helm repo update
kubectl create ns homarr
```

2. set secret for db
kubectl create secret generic db-encryption \
  --from-literal=db-encryption-key='<SECRET_ENCRYPTION_KEY_SECRET_TO_CHANGE>' \
  --namespace homarr

3. install chart 
helm install homarr homarr-labs/homarr -n homarr

4. port-forward
kubectl patch svc homarr -n homarr -p '{"spec":{"type":"NodePort","ports":[{"port":7575,"targetPort":7575,"nodePort":30001}]}}'

### dashy
#### another dashboard

1. install repo
```
helm repo add selfhosted-helmcharts https://vyrtualsynthese.github.io/selfhosted-helmcharts/
helm repo update
```

2. create namespace
kubectl create ns dashy

3. install chart
helm install dashy selfhosted-helmcharts/dashy -n dashy 

4. port-forward
kubectl patch svc dashy -n dashy -p '{"spec":{"type":"NodePort","ports":[{"port":8080,"targetPort":8080,"nodePort":30002}]}}'

### dash 
#### this app shows system resourses to homarr

1. install repo
```
helm repo add oben01 https://oben01.github.io/charts/
helm repo update
```

2. install chart
helm install dash oben01/dashdot --namespace dash --create-namespace

3. port-forward
kubectl patch svc dash-dashdot -n dash -p '{"spec":{"type":"NodePort","ports":[{"port":3001,"targetPort":3001,"nodePort":30003}]}}'

### nextcloud
#### the best cloud storage, but bloated

1. add repo
helm repo add nextcloud https://nextcloud.github.io/helm/
helm repo update

1.1 change password in values

2. install chart
helm upgrade --install nextcloud nextcloud/nextcloud -n nextcloud --create-namespace -f nextcloud/values.yaml

3. set db passs
export APP_HOST=127.0.0.1
export APP_PASSWORD=$(kubectl get secret --namespace nextcloud nextcloud -o jsonpath="{.data.nextcloud-password}" | base64 --decode)

## PLEASE UPDATE THE EXTERNAL DATABASE CONNECTION PARAMETERS IN THE FOLLOWING COMMAND AS NEEDED ##

helm upgrade nextcloud nextcloud/nextcloud -n nextcloud \
  --set nextcloud.password=$APP_PASSWORD,nextcloud.host=$APP_HOST,service.type=ClusterIP,mariadb.enabled=false,externalDatabase.user=nextcloud,externalDatabase.database=nextcloud,externalDatabase.host=YOUR_EXTERNAL_DATABASE_HOST

4.patch svc
kubectl patch svc nextcloud -n nextcloud -p '{"spec":{"type":"NodePort","ports":[{"port":8080,"targetPort":80,"nodePort":30006}]}}'

### seafile
#### less resourse consuming cloud storage

1. install chart
helm upgrade --install seafile oci://registry-1.docker.io/londinzer/seafile --version 0.1.0 -n seafile --create-namespace -f seafile/values.yaml 

2. forward
kubectl patch svc seafile -n seafile -p '{"spec":{"type":"NodePort","ports":[{"port":80,"targetPort":80,"nodePort":30004}]}}'

### navidrome
#### svc for my music

1. install repo 
helm repo add navidrome https://andrewmichaelsmith.github.io/navidrome
helm repo update

2. make pvc for percistance
kubectl apply -f navidrome/pvc.yaml

3. install chart
helm upgrade --install navidrome navidrome/navidrome -n navidrome --create-namespace -f navidrome/values.yaml

4. patch svc
kubectl patch svc navidrome -n navidrome -p '{"spec":{"type":"NodePort","ports":[{"port":4533,"targetPort":4533,"nodePort":30005}]}}'

### openbao
#### vashicorp vault analog with mpl license

1. install repo
helm repo add openbao https://openbao.github.io/openbao-helm
helm repo update

2. install chart
helm upgrade --install openbao openbao/openbao -n openbao --create-namespace -f openbao/values.yaml

3. patch svc
kubectl patch svc openbao -n openbao -p '{"spec":{"type":"NodePort","ports":[{"port":8200,"targetPort":8200,"nodePort":30007}]}}'

### tailscale 
#### for accessing my servers and services outside my network

1. create namespace
kubectl create namespace tailscale

2. generate auth key https://tailscale.com/kb/1185/kubernetes#setup

3. go to tailscale dir and clone official repo
cd k8s/tailscale
git clone https://github.com/tailscale/tailscale.git

4. go to k8s dir
cd tailscale/tailscale/docs/k8s/

5. make rbac 
export SA_NAME=tailscale
export TS_KUBE_SECRET=tailscale-auth
make rbac | kubectl apply -f- -n tailscale

6. create secret with auth key froy step 2
kubectl create secret generic tailscale-auth -n tailscale \
  --from-literal=TS_AUTHKEY=tskey-auth-qwerty1234567 # <- change key from step 2

7. get back and deploy tailscale (change subnets line 36)
cd ../../../..
kubectl apply -f tailscale/subnet-router.yaml

8. open https://login.tailscale.com/admin/machines and look for new machine

9. allow all subnets in web interface

### temp checker 
#### this apps check my nodes temperature every 5 sec, if any node temp > 60, i get telegram message

1. cd temp_checker

2. cp and change example.env
cp example.env .env

3. export thermal files (find thermal zone cpu by comparison with htop/btop) 
docker run -d --rm \
    -p 8080:8080 \
    -v /sys/class/thermal:/sys/class/thermal:ro \
    --privileged \
    --name temp_exporter \
    -e DIR=/sys/class/thermal/thermal_zone2 \
    -e PORT=8080 \
	tonkaxxx/temp_exporter:latest

**docker deployment**

1. use this command in .env file dir
docker run -d --rm \
  -p 8013:8013 \
  --name temp-checker \
  --env-file .env \ 
  --restart unless-stopped \
  tonkaxxx/temp_checker:latest

**kubernetes deployment**

1. cp and change k8s/temp_checker/example_secrets.yaml
cp k8s/temp_checker/example_secrets.yaml k8s/temp_checker/secrets.yaml 

2. kubectl apply -f k8s/temp_checker/secrets.yaml 

3. kubectl apply -f k8s/temp_checker/deployment_and_svc.yaml 

### argocd
#### for automated deployment, recovery, and git synced k8s management.

1. create ns and install argo
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

2. patch svc
kubectl patch service argocd-server -n argocd -p '{"spec": {"type": "NodePort", "ports": [{"name": "http", "port": 80, "targetPort": 8080, "nodePort": 30008}, {"name": "https", "port": 443, "targetPort": 8443, "nodePort": 30443}]}}'

3. get password and copy
kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 --decode && echo

4. go to https://UR_NODE_IP:30008 and login with `admin` and `password from step 3`

### sonarqube
#### for my ci pipeline

1. add repo
helm repo add sonarqube https://SonarSource.github.io/helm-chart-sonarqube
helm repo update

2. kubectl create namespace sonarqube

3. create secret and change the password
kubectl -n sonarqube create secret generic sonar-password \
  --from-literal=sonar-password=YOUR_SUPER_SECRET_PASSWORD

4. install chart 
helm upgrade --install sonarqube sonarqube/sonarqube -n sonarqube --create-namespace -f sonarqube/values.yaml 

5. kubectl patch svc sonarqube-sonarqube -n sonarqube -p '{"spec":{"type":"NodePort","ports":[{"port":9000,"nodePort":30009}]}}'
