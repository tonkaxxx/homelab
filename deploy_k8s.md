## how to deploy k8s cluster with kubeadm

0. disable swap (all nodes)
sudo  cp -av /etc/fstab /etc/fstab.bak
sudo sed -i '/swap/s/^/#/' /etc/fstab
sudo swapoff -a

1. install containerd (all nodes)

2. install cubeadm, kubelet, kubectl (all nodes) 

3. enable kernel module (all nodes)
sudo modprobe br_netfilter
echo "br_netfilter" | sudo tee /etc/modules-load.d/k8s.conf

4. change sisctl params (all nodes) 
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

5. enable SystemdCgroup (all nodes)
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

6. init cluster with cidr for flannel (master node)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 

after copy join command

7. cp config on master (master node)
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config 

8. cp config on ur pc
scp m108@10.5.1.32:/home/m108/.kube/config /home/user/.kube/config

9. apply flannel
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml 

10. join worker (worker node)

### enable metrics (optional)

1. apply metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml --server-side

2. edit deployment to accept ss certs
kubectl edit deployment metrics-server -n kube-system

edit args in deployment:
- --kubelet-insecure-tls
- --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname

3. test 
kubectl top nodes

## how to deplpy longhorn

1. upd repo 
helm repo add longhorn https://charts.longhorn.io
helm repo update

2. apply chart
helm install longhorn longhorn/longhorn --namespace longhorn-system --create-namespace 

3. test web ui
kubectl port-forward -n longhorn-system svc/longhorn-frontend 8080:80

### test postgres (no sharding)

1. apply manifests
kubectl apply -f ./no_sharding/longhorn-pvc.yaml  
kubectl apply -f ./no_sharding/postgres.yaml

2. enter postgres bash
kubectl -n postgres exec -it postgres-7d944b87c5-cwm8p -- bash

3. create sample data
psql -U admin -d mydb

CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(100), created_at TIMESTAMP DEFAULT NOW(), date_column INT);
INSERT INTO test_table (date_column) VALUES (2025-07-25);
SELECT * FROM test_table;	

4. test by deleting pod

## how to deploy postgres with sharding

1. create namespase and  apply manifests
kubectl create namespace postgres
kubectl apply -f citus-coordinator.yaml -n postgres 
kubectl apply -f citus-workers.yaml -n postgres 

2. enter db
kubectl exec -it citus-coordinator-0 -n postgres -- psql -U citus -d citus

3. add citus node (if u have more shards, add them all)
SELECT * from master_add_node('citus-worker-0.citus-worker', 5432);
SELECT * from master_add_node('citus-worker-1.citus-worker', 5432);

4. check nodes
SELECT * FROM master_get_active_worker_nodes();

#### next steps may vary to ur needs
### hot to test
1. create table 
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL
);

2. make shards
SELECT create_distributed_table('users', 'id');

2. or make ref table (copy)
SELECT create_reference_table('users');

3. insert sample data
INSERT INTO users (user_id, username) 
VALUES (123, 'admin'),
       (456, 'user'),
       (789, 'test');

4. get data
EXPLAIN (ANALYZE) 
SELECT * FROM users WHERE user_id = 456;

5. get all shads
SELECT shardid, nodename, nodeport 
FROM pg_dist_shard_placement;

6. get data from shard (look for shard_id in step 4)
kubectl exec citus-worker-0 -n postgres -- psql -U citus -d citus -c "SELECT * FROM users_102008"





## hot to remove 1 node

1. worker
sudo kubeadm reset -f
sudo rm -rf /etc/kubernetes /var/lib/etcd /var/lib/kubelet /var/lib/cni /etc/cni /var/run/kubernetes ~/.kube

2. master
kubectl drain worker1 --ignore-daemonsets --delete-emptydir-data
kubectl delete node worker1

## how to purge cluster 

1. all nodes
sudo kubeadm reset -f
sudo rm -rf /etc/kubernetes /var/lib/etcd /var/lib/kubelet /var/lib/cni /etc/cni /var/run/kubernetes ~/.kube




## troubleshooting

### coredns pending

1. all nodes
sudo systemctl restart kubelet containerd

### self-restarting kube-proxy and kube-flannel

1. on problem node
sudo systemctl enable --now containerd
