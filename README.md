# Weather Tracker
This repository provides a pipeline that stores real-time weather data for a chosen location in an [Amazon S3 bucket](https://aws.amazon.com/fr/s3/).

![API weather + airflow in Kube + S3 Bucket drawio](https://github.com/user-attachments/assets/bbd1d3ef-dedc-4852-bb8e-7a19d859f99c)

## Prerequisites
To use this repository, you need the following installed locally:
- [Python 3](https://www.python.org/downloads/)
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

## (Optional) Set-Up Kubernetes Dashboard

Apply the configurations: 
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl apply -f dashboard-adminuser.yaml
kubectl apply -f dashboard-clusterrolebinding.yaml
```
Run commands to get a token and run the dashboard:
```bash
kubectl -n kubernetes-dashboard create token admin-user
kubectl proxy
```
Then, go to http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/ and use the token you have got in your terminal to access to the Kubernetes Dashboard.
There, you'll soon be able to review and manage all Airflow pods and deployments running in Kubernetes by choosing airflow as your namespace.
Open a new terminal window to set up Airflow.

## Set-Up Airflow
```bash
kubectl create ns airflow
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm install airflow apache-airflow/airflow --namespace airflow --debug
kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow
```
You can already access the Airflow web server from your web browser with the url http://localhost:8080. The password and user name are both set to “admin”.

Open a new terminal window.
Update the file [values.yaml](airflow-config/values.yaml), replacing the actual webserverSecretKey by the result of this command:
```bash
kubectl get secret --namespace airflow airflow-fernet-key -o jsonpath="{.data.fernet-key}" | base64 --decode
```

Now, you can update.
```bash
helm upgrade --install airflow apache-airflow/airflow -n airflow -f airflow-config/values.yaml --debug
```
### Airflow Variables
It's almost finished setting up. Before to activate the pipeline DAG, you need to add the following variables to your [Airflow web server's variables](http://localhost:8080/variable/list/):
- **(Optional) CITY**: *By default, it's “Los Angeles,United States of America”.*
- **API_KEY**: *You can get it subscribing for free at [weatherapi.com](https://www.weatherapi.com/signup.aspx)*
- **ACCESS_KEY_ID and SECRET_ACCESS_KEY**: *You need to create an access key for a user AWS (see below for details).*

###### 1) Create a [AWS account](https://aws.amazon.com/).

###### 2) Create a S3 bucket called “weather-tracker-bucket”.

###### 3) Create a policy using the following JSON:
```JSON
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::weather-tracker-bucket",
                "arn:aws:s3:::weather-tracker-bucket/*"
            ]
        }
    ]
}
```

###### 4) Create a user (e.g. “admin-user”) assigning the policy you've just created.

###### 5) Add an access key and copy-past the values in your [Airflow variables](http://localhost:8080/variable/list/).

In the end, you should have something that looks like this:
![Capture d’écran du 2024-09-05 18-33-27](https://github.com/user-attachments/assets/820661f8-49c8-4853-8708-1112af4c664b)

Finally, activate the DAG to trigger it and watch your bucket fill up little by little over time (every 15 minutes).
![Capture d’écran du 2024-09-05 19-23-35](https://github.com/user-attachments/assets/1958c735-d66c-4aef-b00f-63f827a500e9)


## Additional Code Snippets

```bash
python3 -m venv venv
source venv/bin/activate

kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl delete -f dashboard-adminuser.yaml
kubectl delete -f dashboard-clusterrolebinding.yaml
helm uninstall airflow  --namespace airflow
kubectl delete namespace airflow
```

## Author
Fabrice Mlili

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
