from lib import EmbeddingsClient, CloudSQLClient, Message

class IngestController():
    def __init__(self, sql: CloudSQLClient, emb: EmbeddingsClient):
        self.sql = sql
        self.emb = emb
    
    def upsert_from_json(self, conversations):
        def parse_message(json):
            role = json['role']
            function_name = None
            if 'function_call' in json:
                content = json['function_call']['arguments']
                function_name = json['function_call']['name']
            else:
                content = json['content'].strip("\n")
            if role == 'function':
                function_name = json['name']
            return role, content, function_name
        
        upserts = []
        to_vectorize = []
        for conv_key in conversations:
            conversation = conversations[conv_key]
            for message in conversation:
                role, content, function_name = parse_message(message)
                if role == 'system':
                    continue
                else:
                    to_vectorize.append(content)
                    upserts.append({'role':role, 'message':content, 'function_name':function_name, 'conversation':conv_key})
        
        
        print(f"parsed {len(upserts)} messages. Vectorizing...")
        vectors = self.emb.embed_multiple(to_vectorize)
        print(f"vectorized {len(vectors)} messages. Upserting...")

        rows = [
            Message(role=u['role'], message=u['message'], function_name=u['function_name'], conversation=u['conversation'], embedding=vectors[i])
            for i, u in enumerate(upserts)
        ]

        session = self.sql.get_session()
        session.add_all(rows)
        session.commit()
        session.close()
        print(f"Upserted all messages")
        

