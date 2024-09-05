```bash
git clone https://github.com/fabricemlili/weather-tracker.git
cd weather-tracker
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt -y

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f dashboard-adminuser.yaml
kubectl apply -f dashboard-clusterrolebinding.yaml
kubectl -n kubernetes-dashboard create token admin-user
kubectl proxy

kubectl create ns airflow
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm install airflow apache-airflow/airflow --namespace airflow --debug
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow

kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode
helm upgrade --install airflow apache-airflow/airflow -n airflow -f airflow-config/values.yaml --debug


helm uninstall airflow  --namespace airflow
```