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
