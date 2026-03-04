RAG Caching and Cache Invalidation Demo

This project is a small prototype showing how caching can be added to a RAG system and how to generate cached results when documents change.

The goal is to reduce repeated work for the same queries while avoiding stale answers after document updates.

Approach

The system loads documents from a folder and splits them into paragraphs. Each paragraph can be retrieved if it shares words with the user query.

The system follows a simple flow:

1. Load documents and compute a version hash for each document.
2. Retrieve the most relevant paragraphs for the query.
3. Generate a response using the retrieved text.
4. Use caching to avoid repeating the same work for identical queries.

To demonstrate document updates, the project uses two folders:
- Docs-Version1 which holds the original documents
- Docs-Version2 which holds the updated documents, specifically the cats doc and the healthyfoods doc

Key Decisions

- Use simple hash based document versioning to detect document changes
- Use two separate caches for retrieval and response
- Include context hash and prompt version in the response cache key to prevent stale responses

TradeOffs

To keep the implementation simple the cache is implemented as an in-memory dictionary. This works well for a small demo, but it would not work well in a real system with multiple servers or large amounts of data.
