# Weather Tracker
This repository provides a pipeline that stores real-time weather data for a chosen location in an [Amazon S3 bucket](https://aws.amazon.com/fr/s3/).

## Prerequisites
To use this repository, you need the following installed locally:
- Python 3
- [Docker Desktop](https://docs.docker.com/desktop/) (What I used to run Kubernetes)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [helm](https://helm.sh/docs/intro/install/)
  
Don't forget to activate Kubernetes in the Docker Desktop settings.
  
### Python Requirements
Theses Python packages are used to run the pipeline:
- apache-airflow
- boto3
- pandas

To install them, use the following command:
```bash
pip install -r requirements.txt
```



## Get Started
To use the script, follow these steps:

###### 1) Clone the repository or download the script.
```bash
git clone https://github.com/fabricemlili/weather-tracker.git
```

###### 2) Navigate to the script's directory.
```bash
cd weather-tracker
```

###### 3) (Optional) If you have already installed kubectl and it is pointing to some other environment, such as minikube or a GKE cluster, ensure you change the context so that kubectl is pointing to docker-desktop:
```bash
kubectl config get-contexts
kubectl config use-context docker-desktop
```

## Set-Up Kubernetes Dashboard

(Optional) Apply the configurations: 
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f dashboard-adminuser.yaml
kubectl apply -f dashboard-clusterrolebinding.yaml

kubectl -n kubernetes-dashboard create token admin-user
kubectl proxy
```

## Set-Up Airflow
```bash
kubectl create ns airflow
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm install airflow apache-airflow/airflow --namespace airflow --debug
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```
Upgrade + values.YAML
```bash
kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode
helm upgrade --install airflow apache-airflow/airflow -n airflow -f airflow-config/values.yaml --debug
```


## To Reset

```bash
python3 -m venv venv
source venv/bin/activate

kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl delete -f dashboard-adminuser.yaml
kubectl delete -f dashboard-clusterrolebinding.yaml
helm uninstall airflow  --namespace airflow
kubectl delete namespace airflow
```
