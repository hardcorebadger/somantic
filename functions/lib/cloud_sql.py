from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from .models import *
from sqlalchemy import select, or_, and_
from sqlalchemy.sql import func
from .vector_cloud import VectorCloud
 
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
        self.session_maker = None

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
    
    def get_session(self):
        if not self.db:
            self.connector = Connector()
            self.db = self.__init_pool(self.connector)
            self.session_maker = sessionmaker(bind=self.db)
        return self.session_maker()
    
    def connect(self):
        if not self.db:
            self.connector = Connector()
            self.db = self.__init_pool(self.connector)
            self.session_maker = sessionmaker(bind=self.db)
        return self.db.connect()

    def bootstrap_models(self):
        session = self.get_session()
        Base.metadata.drop_all(self.db)
        Base.metadata.create_all(self.db)
        session.close()
    
    def get_pn_similars(self, positive, pcut, negative, ncut):
        session = self.get_session()
        res = session.query(Message.message, Message.embedding.cosine_distance(positive), Message.embedding.cosine_distance(negative)).filter(Message.embedding.cosine_distance(positive) < pcut).filter(Message.embedding.cosine_distance(negative) > ncut).order_by(Message.embedding.cosine_distance(positive)).all()
        return [{'message':m[0], 'pos':(1-m[1]), 'neg': (1-m[2])} 
                for m in res]
    
    def query_vector_cloud(self, cloud: VectorCloud, cutoff=0.2, role='user'):
        positive, nuances = cloud.get_vectors()
        
        # Extract conditions
        nuance_conditions = [Message.embedding.cosine_distance(positive) - Message.embedding.cosine_distance(n) < 0 for n in nuances]
        nuance_selects = [Message.embedding.cosine_distance(positive) - Message.embedding.cosine_distance(n) for n in nuances]

        session = self.get_session()
        main_similarity = Message.embedding.cosine_distance(positive)
        q = session.query(
            Message.message, 
            main_similarity.label("main_similarity"),
            *nuance_selects
        )        
        # Apply filters
        q = q.filter(Message.role == role)
        q = q.filter(main_similarity < cutoff)
        q = q.filter(and_(*nuance_conditions))
        q = q.order_by(main_similarity)

        results = [{'message':m[0], 'similarity': m[1], 'diffs': [m[2+i] for i, n in enumerate(nuances)]} 
                for m in q.all()]
        return {"count": len(results), "results":results}

    def get_compound_similars(self, ps, ns, role='user'):
        session = self.get_session()
        q = session.query(Message.message)
        q = q.filter(Message.role == role)
        for p in ps:
            print(p[1])
            q = q.filter(Message.embedding.cosine_distance(p[0]) < p[1])
        for n in ns:
            print(n[1])
            q = q.filter(Message.embedding.cosine_distance(n[0]) > n[1])
        results = [{'message':m[0]} 
                for m in q.all()]
        return {"count": len(results), "results":results}

    def get_similar_messages(self, vector):
        session = self.get_session()
        return [{'message':m[0], 'similarity':(1-m[1])} 
                for m in 
                session.query(Message.message, Message.embedding.cosine_distance(vector)).order_by(Message.embedding.cosine_distance(vector)).all()]

    def get_avg(self):
        session = self.get_session()
        return session.scalars(select(func.avg(Message.embedding))).first()
    
    def get_compound_similarity_messages(self, positive, negative):
        session = self.get_session()
        return [{'message':m[0], 'similarity':(m[1])} 
                for m in 
                session.query(Message.message, (1-Message.embedding.cosine_distance(positive)) - (1-Message.embedding.cosine_distance(negative))).order_by((1-Message.embedding.cosine_distance(positive)) -(1-Message.embedding.cosine_distance(negative))).all()]
