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

    @api.post("/debug")
    def debug():
        # conversations = load_conversations()
        # ingest.upsert_from_json(conversations)
        # sql.bootstrap_models()
        # test_upsert(sql, emb)
        # return sql.get_avg()
        # r = get_sim(sql, "I'm confused")
        # q = emb.get_average([
        #     "Why is it moving",
        #     "Why is it up",
        #     "Why is it down",
        #     "Why is NVDA moving",
        #     "Why is TSLA moving",
        #     "Why is LXR moving"
        # ])
        # p = emb.get_average([
        #     "I couldn't find any information",
        #     "Based on the information available, it seems there is no specific data or information regarding the removal of gains from a free riding violation. If you have any further questions or need assistance with a different topic, feel free to ask!"
        #     "I couldn't find any specific predictions for the price of this stock in one week. Stock price predictions can vary and are often speculative in nature. It's important to conduct thorough research and consider various factors before making any investment decisions."
        #     "I couldn't find specific information on the float of this stock at the moment. If you have any other questions or need information on a different stock, feel free to ask!"
        # ])
        # n = emb.get_average([
        #     "What do you want to know about this stock?",
        #     "Will my gains from free riding violation be removed",
        #     "Do you see any recent news that might help explain the recent changes?",
        #     "There are currently no Bitcoin-focused ETFs available on Public.com. If you have any other questions or need information on a different topic, feel free to ask!"
        # ])

        # no_relevant_info = Blob()
        # no_relevant_info.add_cloud([
        #     "I couldn't find any information",
        #     "Based on the information available, it seems there is no specific data or information regarding"
        #     "I couldn't find any specific"
        #     "I couldn't find specific information"
        # ])
        # no_relevant_info.sub_cloud(["I'm unable to provide a that as it falls outside the scope of stock market-related information."], 0.15)
        # no_relevant_info.sub_cloud(["I can't provide financial advice or recommendations, including whether to buy, sell, or hold a specific asset."], 0.15)
        # no_relevant_info = emb.embed_blob(no_relevant_info)
        # print(no_relevant_info)
        # q = AVG_IDK
        # return sql.get_pn_similars(p, 0.19, n, 0.10), 200
        
        # blob.add_cloud([
        #     "When is their next earnings call?",
        #     "What date is their next earnings call?",
        #     "When do they announce earnings?",
        #     "Whats the next earnings report date?"
        # ], 0.177)
        # blob.sub_cloud([
        #     "Why is this stock moving?",
        #     "When is their next earnings call?",
        #     "What did they say in their earnings call?",
        #     "What does this company do",
        #     "Top movers in the market today"
        # ], 0.1)
        # blob.sub_cloud([
        #     "When is their next earnings call?",
        #     "what else this week has impacted it specifically?",
        #     "What guidance did they give in their most recent earnings call?",
        #     "Why is RSI moving?"
        # ], 0.18)
        # blob.sub_cloud([
        #     "Summarize their most recent earnings",
        #     "How did they most recent earnings turn out",
        #     "What guidance did they give in their most recent earnings",
        #     "When was their most recent earnings"
        # ], 0.0)

        # blob.add_cloud([
        #     "Will the price increase?",
        #     "What will the price be in 1 week?",
        #     "Can the price hit $10k by the end of the month?",
        #     "Thoughts on price outlook?",
        #     "When will the price go back up"
        # ])
        # blob.sub_cloud([
        #     "Why is share price increasing",
        #     "What is the current market analysis",
        #     "What are some pros and cons of this investment?"
        # ])
        # blob.sub_cloud([
        #     "Explain balanced analysis for why I would or wouldn't buy this stock"
        #     "Pros and cons of investing",
        # ], 0.18)

        # blob.add_cloud([
        #     "Recommend me specific financial assets to buy",
        #     "Best crypto to buy",
        #     "Best stocks to buy",
        # ])
        # blob.sub_cloud([
        #     "Which bitcoin equities allow $50.00 investments",
        #     "Top volume stocks",
        #     "Top movers in th stock market today"
        # ], 0.18)
        # blob.sub_cloud([
        #     "When is their next earnings call?",
        # ], 0.15)
        # blob.sub_cloud([
        #     "What stocks have unsual trade volume today?"
        # ], 0.15)
        # return blob.get_clouds()
        # cloud = VectorCloud(emb, [
        #     "Will the price increase?",
        #     "What will the price be in 1 week?",
        #     "Can the price hit $10k by the end of the month?",
        #     "Thoughts on price outlook?",
        #     "When will the price go back up"
        # ])
        # cloud.add_nuance([
        #     "Why is share price increasing",
        #     "What is the current market analysis",
        #     "What are some pros and cons of this investment?"
        # ])
        # cloud.add_nuance([
        #     "When is their next earnings call?"
        # ])
        cloud = VectorCloud(emb, [
            "Why is it moving?"
            "Why is it up today?",
            "Why is it down today?",
            "Whats causing current price movement?",
            "Why is XXXX moving?"
        ])
        cloud.add_nuance(["What are the latest top movers?"])
        cloud.add_nuance(["Is it gonna go up or is it gonna stagnant?"])
        cloud.add_nuance(["What is the current market analysis"])
        return sql.query_vector_cloud(cloud, 0.17, 'user')
        return 'success', 200
        
        # return get_sim(sql, "Bring me to your leader"), 200

    with api.request_context(req.environ):
        return api.full_dispatch_request()

