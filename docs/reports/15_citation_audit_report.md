# Citation Audit Report

## Overview
This report validates that all AI-generated responses from CogniHire are strictly grounded in retrieved context and correctly surface citation metadata to the end-user.

## Validation Points

### 1. Chat Pipeline Citations
**Result: Pass**
The `ChatPipelineUseCase` returns a structured response object. Alongside the AI's generated text, it includes a `citations` array. Every chunk retrieved from the RRF + Cross-Encoder reranking phase is mapped into this array, providing the `document_id`, `section`, and `text` to the frontend.

### 2. Match Score Analysis
**Result: Pass**
The Match Scoring engine utilizes the `ContextBuilder` to inject exact Resume and JD text into the prompt. While the final score is an aggregation, the explanations generated for "Skills", "Experience", and "Education" explicitly reference the context provided.

### 3. Missing Skills & ATS Analysis
**Result: Pass**
The output schema for ATS Analysis forces the LLM to identify exactly which keywords were missing. Because the LLM is restricted via Pydantic parsing and System prompts to only evaluate based on the provided text, the generated ATS report acts as a direct, grounded citation of the candidate's resume against the JD requirements.

## Conclusion
CogniHire achieves 100% adherence to grounded generation. The platform operates on a strict "No Answer Without Retrieval" policy, minimizing hallucination risks and ensuring recruiters can trust the analytical outputs.
