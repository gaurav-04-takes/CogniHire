# 25 — Glossary

| Term | Definition |
|------|------------|
| **ATS** | **Applicant Tracking System**. Software used by recruiters to manage job applications. Traditional ATS rely on keyword parsing, which CogniHire aims to improve upon with semantic search. |
| **BGE** | **BAAI General Embedding**. A family of high-performance embedding models. *Note: CogniHire's code references BGE in class names, but uses Gemini embeddings under the hood.* |
| **BM25** | **Best Matching 25**. A popular keyword-based retrieval algorithm that scores documents based on term frequency and inverse document frequency. |
| **ChromaDB** | The open-source vector database used by CogniHire to store and retrieve document embeddings. |
| **Chunking** | The process of splitting large documents into smaller text segments (chunks) to fit within LLM context windows and improve retrieval accuracy. |
| **Clean Architecture** | A software design philosophy that separates concerns into layers, with dependencies strictly pointing inward toward pure domain logic. |
| **Cross-Encoder** | A model that takes two texts (e.g., query and chunk) simultaneously and outputs a similarity score. Slower but more accurate than bi-encoders (embeddings). |
| **Dependency Injection (DI)** | A design pattern where objects are passed their dependencies (e.g., database connections) rather than creating them internally. Used heavily in CogniHire. |
| **Embedding** | A numerical representation (vector) of text capturing its semantic meaning. Used to find similar text via mathematical distance. |
| **FastAPI** | The modern, fast Python web framework used for CogniHire's backend API. |
| **Gemini** | Google's large language model, used by CogniHire for text generation and embeddings. |
| **LLM** | **Large Language Model**. E.g., Gemini, GPT-4. |
| **Pydantic** | A Python data validation library used to define robust data schemas (used extensively in FastAPI routes and analysis outputs). |
| **RAG** | **Retrieval-Augmented Generation**. A technique where an LLM is provided with factual context retrieved from a database before generating an answer. |
| **RAGAS** | **Retrieval Augmented Generation Assessment**. A framework for evaluating the quality of RAG systems using metrics like Faithfulness and Answer Relevancy. |
| **RRF** | **Reciprocal Rank Fusion**. An algorithm that combines ranked result lists from multiple retrievers (e.g., Vector + BM25) into a single unified ranking without relying on arbitrary scores. |
| **SSE** | **Server-Sent Events**. A protocol for one-way, real-time data streaming from server to client. Used for the chat streaming endpoint. |
| **Streamlit** | A Python framework for rapidly building web applications, used for CogniHire's frontend UI. |
| **Vector Search** | Retrieving documents by finding the closest embedding vectors in a high-dimensional space (semantic similarity). |

---

> **Next**: [Known Limitations](26_KNOWN_LIMITATIONS.md)
