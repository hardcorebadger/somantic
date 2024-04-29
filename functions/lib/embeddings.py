from openai import OpenAI

class EmbeddingsClient():
    def __init__(self, openai_key):
        self.client = OpenAI(
            api_key=openai_key
        )
    
    def __completion(self, input):
        return self.client.embeddings.create(
            input=input,
            model="text-embedding-ada-002"
        )

    def embed(self, input):
        return self.__completion(input).data[0].embedding
    
    def embed_multiple(self, input):
        response = self.__completion(input)
        return [d.embedding for d in response.data]
    
    def embed_multiple_zipped(self, input):
        response = self.__completion(input)
        return [(input[i], d.embedding) for i, d in enumerate(response.data)]
    
    def get_average(self, input):
        vectors = self.embed_multiple(input)
        num_vectors = len(vectors)
        vector_length = len(vectors[0])  # Assuming all vectors have the same length
        average_vector = [0] * vector_length

        for vector in vectors:
            for i, component in enumerate(vector):
                average_vector[i] += component

        # Divide each component by the number of vectors to get the average
        average_vector = [component / num_vectors for component in average_vector]

        return average_vector