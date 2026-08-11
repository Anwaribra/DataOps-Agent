import os
import psycopg2
from dagster import ConfigurableResource, resource

class PostgresResource(ConfigurableResource):
    host: str = os.getenv("POSTGRES_HOST", "localhost")
    port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    user: str = os.getenv("POSTGRES_USER", "dataops_user")
    password: str = os.getenv("POSTGRES_PASSWORD", "dataops_password")
    database: str = os.getenv("POSTGRES_DB", "dataops_db")

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.database
        )
