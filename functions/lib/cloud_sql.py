from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy

class CloudSQLClient():
    def __init__(self, project, region, instance, user, password, databse):
        self.project = project
        self.region = region
        self.instance = instance
        self.user = user
        self.password = password
        self.databse = databse
        self.connector = None
        self.db = None

    def __init_pool(self, connector):
        def getconn():
            connection = connector.connect(
                f"{self.project}:{self.region}:{self.instance}",
                "pg8000",
                user=self.user,
                password=self.password,
                db=self.databse,
                ip_type=IPTypes.PUBLIC,  #IPTypes.PRIVATE for Private IP
            )
            return connection

        # create connection pool
        engine = sqlalchemy.create_engine("postgresql+pg8000://", creator=getconn)
        return engine

    def query(self, query):
        if not self.db:
            self.connector = Connector()
            self.db = self.__init_pool(self.connector)
        # build connection for db using Python Connector
        with self.db.connect() as conn:
            result = conn.execute(sqlalchemy.text(query)).fetchone()
        return str(result[0])