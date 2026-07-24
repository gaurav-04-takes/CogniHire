# CogniHire Architecture

CogniHire utilizes a Clean Architecture approach to strictly separate concerns, ensuring maximum maintainability and testability.

## Clean Architecture Layers

```mermaid
graph TD
    subgraph Infrastructure
        ChromaDB[(ChromaDB)]
        SQLite[(SQLite DB)]
        Gemini[Google Gemini API]
        BGE[BGE-M3 Embedder]
        PDF[PyMuPDF]
    end

    subgraph API
        Upload[Upload Router]
        ChatAPI[Chat Router]
        AnalyzeAPI[Analysis Router]
    end

    subgraph Application
        IngestUC[IngestDocumentUseCase]
        ChatUC[ChatPipelineUseCase]
        HiringUC[HiringAnalysisUseCase]
        
        AnalyzeAPI --> HiringUC
        ChatAPI --> ChatUC
        Upload --> IngestUC
    end

    subgraph Domain
        Interfaces[Core Interfaces]
        Entities[Core Entities]
        
        IngestUC --> Interfaces
        ChatUC --> Interfaces
        HiringUC --> Interfaces
    end
    
    Infrastructure -. implements .-> Interfaces
```

## Retrieval Pipeline

```mermaid
sequenceDiagram
    participant User
    participant ChatUC as ChatPipeline
    participant QR as QueryRewriter
    participant VR as VectorRetriever
    participant BR as BM25Retriever
    participant RRF as RRFRetriever
    participant Rank as CrossEncoderReranker
    
    User->>ChatUC: "What frameworks do they know?"
    ChatUC->>QR: rewrite(query, history)
    QR-->>ChatUC: "Candidate's web frameworks"
    
    ChatUC->>RRF: retrieve("Candidate's web frameworks")
    par Semantic
        RRF->>VR: search(embeddings)
    and Lexical
        RRF->>BR: search(keywords)
    end
    VR-->>RRF: Top 20 Semantic Chunks
    BR-->>RRF: Top 20 Lexical Chunks
    
    RRF->>RRF: Apply Reciprocal Rank Fusion
    RRF-->>ChatUC: Top 20 Fused Chunks
    
    ChatUC->>Rank: rerank(query, Top 20 Chunks)
    Rank-->>ChatUC: Top 5 Highest Fidelity Chunks
```

## RAG Pipeline

```mermaid
sequenceDiagram
    participant ChatUC as ChatPipeline
    participant ContextBuilder
    participant LLM as GeminiProvider
    participant Eval as EvaluationService
    
    ChatUC->>ContextBuilder: build_context(Top 5 Chunks)
    ContextBuilder-->>ChatUC: context_str, citations
    
    ChatUC->>LLM: generate(query, system_prompt, context_str)
    LLM-->>ChatUC: response_text
    
    par Background Task
        ChatUC->>Eval: evaluate(query, response, context)
        Eval->>Eval: Ragas Scoring
    and Sync Return
        ChatUC-->>User: Response + Citations
    end
```
