import boto3
import pymysql
import os
import json

def lambda_handler(event, context):
    # Stage actual (dev, test o prod)
    database = os.environ['DB_NAME']  # Ej: dev/test/prod
    secret_name = f"rds_mysql_alumnos_user_{database}"
    region_name = 'us-east-1'

    # Obtener secreto
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        secret_data = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(secret_data['SecretString'])
    except Exception as e:
        return {"statusCode": 500, "error": f"Error obteniendo secreto: {str(e)}"}

    # Datos de conexión
    user = secret['username']
    password = secret['password']
    host = secret['host']  # Usar host del secreto

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

        return {"statusCode": 200, "body": results}

    except Exception as e:
        return {"statusCode": 500, "error": str(e)}

    finally:
        if 'connection' in locals() and connection:
            connection.close()
