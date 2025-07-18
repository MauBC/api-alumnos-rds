import boto3
import pymysql
import os
import json

def lambda_handler(event, context):
    # Nombre del secreto en Secrets Manager (puede ser pasado como variable de entorno)
    secret_name = os.environ['SECRET_NAME']  # Ej: rds_mysql_alumnos_user_dev
    region_name = os.environ['AWS_REGION']   # Ej: us-east-1

    # Cliente de Secrets Manager
    client = boto3.client('secretsmanager', region_name=region_name)

    # Obtener el secreto
    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret_dict = json.loads(response['SecretString'])
    except Exception as e:
        return {
            "statusCode": 500,
            "error": f"Error obteniendo secreto: {str(e)}"
        }

    # Extraer credenciales
    host = secret_dict['host']
    user = secret_dict['username']
    password = secret_dict['password']
    database = secret_dict['dbname']

    # Conexión a la BD
    connection = None
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            db=database,
            connect_timeout=5
        )

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM alumnos;")
            results = cursor.fetchall()

        return {
            "statusCode": 200,
            "body": results
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }

    finally:
        if connection:
            connection.close()
