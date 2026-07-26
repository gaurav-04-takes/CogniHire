# Multi-Document Isolation Diagram

```mermaid
graph TD
    subgraph "ChromaDB (Collection: 'documents')"
        C1[Chunk 1<br/>doc_id: A (Resume)]
        C2[Chunk 2<br/>doc_id: A (Resume)]
        C3[Chunk 3<br/>doc_id: B (JD)]
        C4[Chunk 4<br/>doc_id: C (Resume)]
    end

    subgraph "Chat Query for Resume A"
        Q1[User: "What are his skills?"]
        F1[Filter: document_id == A]
        Q1 --> F1
        F1 -->|Retrieves| C1
        F1 -->|Retrieves| C2
        F1 -.x|Ignores| C3
        F1 -.x|Ignores| C4
    end

    subgraph "Hiring Analysis (Match Score)"
        Q2[Analyze: Resume A vs JD B]
        F2_A[Filter: document_id == A]
        F2_B[Filter: document_id == B]
        Q2 --> F2_A
        Q2 --> F2_B
        F2_A -->|Retrieves All| C1
        F2_A -->|Retrieves All| C2
        F2_B -->|Retrieves All| C3
    end
```
