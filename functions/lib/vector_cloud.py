from .embeddings import EmbeddingsClient

class VectorCloud():
    def __init__(self, emb: EmbeddingsClient, examples):
        self.emb = emb
        self.examples = examples
        self.nuances = []
        self.example_vector = None
        self.nuance_vectors = None
    
    def add_nuance(self, examples):
        self.nuances.append(examples)
    
    def embed(self):
        self.example_vector = self.emb.get_average(self.examples)
        self.nuance_vectors = []
        for c in self.nuances:
            self.nuance_vectors.append(self.emb.get_average(c))
    
    def get_vectors(self):
        if not self.example_vector:
            self.embed()
        return self.example_vector, self.nuance_vectors