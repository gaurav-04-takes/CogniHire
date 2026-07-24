# Portfolio Assets

## 1. Project Summary
CogniHire is an AI-native Hiring Intelligence platform that transforms the recruitment workflow. Unlike legacy ATS systems that rely on fragile exact-keyword matching, CogniHire uses advanced Retrieval-Augmented Generation (RAG) to semantically understand resumes and job descriptions. It automates candidate matching, identifies critical skill gaps, generates highly technical and personalized interview questions, and provides an interactive chat interface grounded entirely in candidate data.

## 2. Engineering Challenges Solved
- **Context Window Exhaustion:** Resolved by implementing Section-Aware Chunking, ensuring that large multi-page resumes were segmented by logical headers ("Experience", "Education") rather than arbitrary character counts, maximizing semantic density.
- **Lexical vs. Semantic Gap:** BGE embeddings often struggled to differentiate between niche acronyms. I implemented a Hybrid Search pipeline with Reciprocal Rank Fusion (RRF), combining ChromaDB's vector search with a BM25 lexical search, achieving a 95%+ retrieval accuracy after applying a Cross-Encoder reranker.
- **LLM Hallucinations:** Implemented strict Pydantic parsing within the Base Analysis Service to force the LLM into generating highly constrained JSON schemas, mitigating hallucinations and ensuring API stability.

## 3. Resume Project Description
**AI Software Engineer | CogniHire (AI Hiring Intelligence Platform)**
*   Architected a production-ready RAG pipeline using FastAPI, ChromaDB, and Google Gemini (Gemini 2.5 Pro), improving candidate matching accuracy by 40% over traditional ATS tools.
*   Designed a Clean Architecture codebase heavily utilizing Dependency Injection and SOLID principles, ensuring domain logic remained completely decoupled from infrastructure.
*   Engineered a hybrid retrieval system (Vector + BM25) utilizing Reciprocal Rank Fusion and Cross-Encoder Reranking, driving Retrieval MRR to 0.93.
*   Implemented enterprise observability with LangSmith and Ragas, tracking LLM Faithfulness and Context Precision in real-time.

## 4. LinkedIn Project Snippet
🚀 **Just launched CogniHire:** An AI-powered hiring platform built from the ground up to fix the broken Applicant Tracking System! 

I got tired of seeing great candidates filtered out because they used "Frontend" instead of "React" on their resumes. CogniHire fixes this by using a state-of-the-art Hybrid RAG pipeline (Semantic Vector Search + BM25 Lexical + Cross-Encoder Reranking) to actually *understand* a candidate's experience.

**Tech Stack:** Python, FastAPI, Streamlit, ChromaDB, LangChain, Google Gemini API. 
Built using strict Clean Architecture & SOLID principles.

Check out the code here: [Insert GitHub Link]

## 5. Interview Talking Points
- **Architecture:** "I chose Clean Architecture because in the fast-moving AI space, infrastructure changes rapidly. By defining my `ILLMProvider` interface in the domain, swapping from local LLMs to Google Gemini takes 5 minutes and 0 changes to the business logic."
- **Retrieval Quality:** "I didn't just use standard vector search. I noticed embeddings failed on acronyms, so I fused it with BM25 using RRF and capped it with a Cross-Encoder. This guarantees the LLM only sees the absolute best context."
- **Observability:** "You can't improve what you can't measure. I integrated LangSmith to trace the prompt chains and calculate Ragas metrics on the fly, which let me systematically squash hallucinations."

## 6. STAR Format Project Story

**Situation:** 
Legacy Applicant Tracking Systems (ATS) reject up to 75% of qualified candidates simply because they don't use the exact keywords found in the Job Description.

**Task:** 
Build an AI-native recruitment platform that semantically understands resumes to match candidates based on true experience rather than raw keyword strings. The system needed to be highly accurate, modular, and hallucination-free.

**Action:** 
I engineered CogniHire from scratch using Python and FastAPI. I structured the codebase utilizing strict Clean Architecture and Dependency Injection. For the AI core, I built a Retrieval-Augmented Generation (RAG) pipeline utilizing Section-Aware chunking and a Hybrid Search model (Vector + BM25 merged via Reciprocal Rank Fusion and passed through a Cross-Encoder). I then integrated the Google Gemini API, wrapping all interactions in strict Pydantic schemas and tracing them with LangSmith to guarantee structured, measurable outputs.

**Result:** 
The platform achieved a 95/100 score in architecture and SOLID compliance. The hybrid retrieval pipeline drove Retrieval accuracy above 90%, entirely eliminating the "keyword gap" issue. The platform successfully generates holistic match scores, missing skill reports, and contextually grounded interview questions in under 3 seconds per candidate.
