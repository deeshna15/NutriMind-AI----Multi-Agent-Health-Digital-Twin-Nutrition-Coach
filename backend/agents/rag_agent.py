import httpx  # pyrefly: ignore [missing-import]
import json
from typing import Dict, Any

# pyrefly: ignore [missing-import]
import chromadb
# pyrefly: ignore [missing-import]
from chromadb import EmbeddingFunction, Documents, Embeddings

class OllamaEmbeddings(EmbeddingFunction):
    def __init__(self, model_name: str = "llama3.2", ollama_url: str = "http://localhost:11434/api/embed"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    def __call__(self, input: Documents) -> Embeddings:
        try:
            payload = {
                "model": self.model_name,
                "input": input
            }
            # Set timeout=None to allow Ollama to take its time loading the model
            r = httpx.post(self.ollama_url, json=payload, timeout=None)
            if r.status_code == 200:
                data = r.json()
                embeddings = data.get("embeddings")
                if embeddings:
                    return embeddings
            raise Exception(f"Failed to generate embeddings. Status code: {r.status_code}, Response: {r.text}")
        except Exception as e:
            print(f"Ollama embedding generation error: {e}")
            raise e

# Module-level singletons for ChromaDB persistence within process
_chroma_client = None
_embedding_function = None
_collection = None

class RAGAgent:
    def __init__(self):
        global _chroma_client, _embedding_function, _collection
        self.ollama_url = "http://localhost:11434/api/generate"
        
        if _chroma_client is None:
            # Initialize chroma client and custom embedding function once
            _chroma_client = chromadb.EphemeralClient()
            _embedding_function = OllamaEmbeddings(model_name="llama3.2")
            _collection = _chroma_client.get_or_create_collection(
                name="nutrimind_guidelines",
                embedding_function=_embedding_function
            )
            
            # Pre-seed document guidelines to search locally
            self.documents = [
                "WHO recommends that daily sodium intake should not exceed 2000mg to prevent hypertension and cardiac diseases.",
                "USDA guidelines state that a healthy adult should consume at least 5 servings of fruits and vegetables daily.",
                "Consuming more than 15g of added sugar per single food item increases the risk of metabolic syndrome and insulin resistance.",
                "A single meal containing more than 800 calories exceeds optimal portion limits and contributes to unhealthy weight gain.",
                "Eating pizza, fast food, and highly processed meals exceeds safe fat (30g) and sodium (1000mg) thresholds, creating elevated cardiovascular risk.",
                "For muscle gain, a protein intake of 1.6g to 2.2g per kilogram of body weight is optimal.",
                "For blood sugar control in Diabetes or PCOS, carbohydrate intake should be strictly limited to under 120g daily, focusing on low-glycemic index foods.",
                "Consuming high sodium foods elevates blood pressure. Balanced diet compensation requires eating low-sodium, high-potassium foods like spinach and celery.",
                "Junk food consumption (like pizza) should be balanced by light, high-protein, zero-sodium meals such as grilled chicken salad or vegetable tofu stir-fry."
            ]
            
            if _collection.count() == 0:
                ids = [f"guideline_{i}" for i in range(len(self.documents))]
                _collection.add(
                    documents=self.documents,
                    ids=ids
                )
        
        self.collection = _collection

    def retrieve_guidelines(self, query: str) -> str:
        """
        Queries ChromaDB EphemeralClient to retrieve matching guidelines.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=2
            )
            retrieved_docs_list = results.get("documents", [[]])[0]
            if retrieved_docs_list:
                return "\n".join(f"- {doc}" for doc in retrieved_docs_list)
        except Exception as e:
            print(f"Error retrieving guidelines: {e}")
        return "- No specific guideline found."

    def process(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes a user query, retrieves the relevant guidelines via local ChromaDB database query,
        and uses Ollama to generate a grounded answer containing nutritional recommendations and risks.
        """
        if "rag_answer" in state and state["rag_answer"]:
            return state

        # 1. Query ChromaDB Collection dynamically
        retrieved_doc = self.retrieve_guidelines(query)

        # 2. Augmented Generation
        prompt = f"""
        You are an expert nutritionist coach. Answer the user's question or evaluate their food items based strictly on the following official guidelines.
        Ensure your reply outlines:
        - The official nutritional value caps (calories, carbs, sugar, sodium).
        - The long-term disease risk factors (metabolic, blood pressure, etc.) that the meal can cause if it exceeds guidelines.
        - Advice on how they can balance their diet.
        
        Guidelines:
        {retrieved_doc}
        
        Question/Food Items:
        {query}
        
        Return ONLY a JSON object with this exact structure:
        {{
            "answer": "Your grounded response detailing values and risk factors",
            "source": "The specific guidelines you matched"
        }}
        """

        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        # Execute post request to Ollama
        response = httpx.post(self.ollama_url, json=payload, timeout=None)
        if response.status_code == 200:
            data = response.json()
            text = data.get("response", "{}")
            parsed_data = json.loads(text)
            state["rag_answer"] = parsed_data
            
            # Append RAG grounded risks into the state's disease risks
            rag_ans_text = parsed_data.get("answer", "")
            if rag_ans_text:
                state["disease_risk_analysis"].append(f"RAG Grounded Warning: {rag_ans_text[:120]}...")
            return state
        else:
            raise Exception(f"Ollama returned error status code: {response.status_code}")
