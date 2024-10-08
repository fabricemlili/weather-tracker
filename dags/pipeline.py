from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable


def extract_data(**kwargs):
    import requests
    API_KEY=Variable.get("API_KEY")
    try:
        CITY=Variable.get("CITY")
    except:
        CITY="Los Angeles,United States of America"
    url = f'https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        weather_data = response.json()  # Parse the JSON response

        # Save the data to XCom for use in other tasks
        ti = kwargs['ti']
        ti.xcom_push(key='weather_data', value=weather_data)

    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        raise



def upload_data(**kwargs):
    import pandas as pd
    import boto3
    from io import StringIO
    ACCESS_KEY_ID=Variable.get("ACCESS_KEY_ID")
    SECRET_ACCESS_KEY=Variable.get("SECRET_ACCESS_KEY")

    weather_data = kwargs['ti'].xcom_pull(key='weather_data', task_ids='extract_data')
    df = pd.DataFrame({
    "Location": [weather_data['location']['name']],
    "Country": [weather_data['location']['country']],
    "Recorded Time": [weather_data['current']['last_updated']],
    "Temperature (C)": [weather_data['current']['temp_c']],
    "Condition": [weather_data['current']['condition']['text']],
    "Wind Speed (kph)": [weather_data['current']['wind_kph']],
    "Wind Direction": [weather_data['current']['wind_dir']],
    "Humidity (%)": [weather_data['current']['humidity']],
    "Visibility (km)": [weather_data['current']['vis_km']],
    "UV Index": [weather_data['current']['uv']],
    "Pressure (mb)": [weather_data['current']['pressure_mb']]
    })
    print(df)

    # Convert DataFrame to CSV
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    file_path = f"{df['Location'].values[0]}/{df['Recorded Time'].values[0]}.csv"
    s3_client = boto3.client('s3', aws_access_key_id = ACCESS_KEY_ID, aws_secret_access_key = SECRET_ACCESS_KEY)
    try:
        s3_client.put_object(
            Bucket='weather-tracker-bucket',
            Key=file_path,
            Body=csv_buffer.getvalue(),
        )
        print(f"New weather data stored in {file_path}")

    except Exception as e:
        raise RuntimeError(f"Error uploading data to S3: {e}")




default_args = {
    'owner': 'airflow',
    'start_date': datetime.now() - timedelta(hours=1),
    'retries': 3,  
    'retry_delay': timedelta(seconds=30),  
    'catchup': False
}

dag = DAG(
    'get_weather',
    default_args = default_args,
    schedule=timedelta(minutes=15)
)

extract_data_from_url = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

upload_data_from_url = PythonOperator(
    task_id='upload_data',
    python_callable=upload_data,
    dag=dag
)

extract_data_from_url >> upload_data_from_url
