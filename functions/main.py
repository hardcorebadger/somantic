from firebase_admin import initialize_app, firestore
from firebase_functions import https_fn
import flask
import traceback
from lib import ErrorResponse, CloudSQLClient
from tmp_keys import *

# from local_scripts import reset_update_as_of

#################################
# App Initialization
#################################

app = initialize_app()

#################################
# Globals
#################################

sql = CloudSQLClient(SQL_PROJECT, SQL_REGION, SQL_INSTANCE, SQL_USER, SQL_PASS, SQL_DB)

# ##############################
# API
# ##############################

@https_fn.on_request()
def fn_api(req: https_fn.Request) -> https_fn.Response:

    # db = firestore.client(app)
    api = flask.Flask(__name__)

    @api.errorhandler(Exception)
    def invalid_api_usage(e : Exception):
        print(e)
        if isinstance(e, ErrorResponse):
            print(e.to_json())
            return e.respond()
        traceback.print_exc()
        return flask.jsonify({'error': "An unknown error occurred"}), 500

    @api.post("/debug")
    def debug():
        return sql.query("SELECT NOW()"), 200

    with api.request_context(req.environ):
        return api.full_dispatch_request()

