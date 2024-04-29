from firebase_admin import initialize_app, firestore
from firebase_functions import https_fn
import flask
import traceback
from lib import ErrorResponse, CloudSQLClient, EmbeddingsClient, VectorCloud
from tmp_keys import *
from controllers import IngestController
from local_scripts import create_message_table, get_sim, insert_message, test_upsert, load_conversations


#################################
# App Initialization
#################################

app = initialize_app()

#################################
# Globals
#################################

sql = CloudSQLClient(SQL_PROJECT, SQL_REGION, SQL_INSTANCE, SQL_USER, SQL_PASS, SQL_DB)
emb = EmbeddingsClient(OPENAI_API_KEY)
# ##############################
# API
# ##############################

@https_fn.on_request()
def fn_api(req: https_fn.Request) -> https_fn.Response:

    # db = firestore.client(app)
    api = flask.Flask(__name__)
    ingest = IngestController(sql, emb)

    @api.errorhandler(Exception)
    def invalid_api_usage(e : Exception):
        print(e)
        if isinstance(e, ErrorResponse):
            print(e.to_json())
            return e.respond()
        traceback.print_exc()
        return flask.jsonify({'error': "An unknown error occurred"}), 500
    
    @api.post("/cloud-query")
    def cloud_query():
        data = flask.request.get_json()
        cloud = VectorCloud(emb, data['examples'])
        for n in data['nuances']:
            cloud.add_nuance(n)
        return sql.query_vector_cloud(cloud, data['cutoff'], data['role'])

    @api.post("/debug")
    def debug():
        # conversations = load_conversations()
        # ingest.upsert_from_json(conversations)
        # sql.bootstrap_models()
        return 'success', 200
        
        # return get_sim(sql, "Bring me to your leader"), 200

    with api.request_context(req.environ):
        return api.full_dispatch_request()

