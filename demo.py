from cache import SimpleCache
from rag import (
    load_docs,
    retrieve,
    generate_answer,
    retrieval_cache_key,
    response_cache_key,
    context_hash
)


def ask(query, docs, filters, retrieval_cache, response_cache):

    r_key = retrieval_cache_key(query, filters)
    chunks = retrieval_cache.get(r_key)

    if chunks is None:
        print("[retrieval] MISS")
        chunks = retrieve(query, docs, k=2)
        retrieval_cache.set(r_key, chunks)
    else:
        print("[retrieval] HIT")

    ctx = context_hash(chunks)
    a_key = response_cache_key(query, ctx)
    answer = response_cache.get(a_key)

    if answer is None:
        print("[response ] MISS")
        answer = generate_answer(query, chunks)
        response_cache.set(a_key, answer)
    else:
        print("[response ] HIT")

    print(answer)
    print()


def run(folder):

    docs, corpus_version = load_docs(folder)

    print()
    print("Corpus:", folder)
    print("corpus_version =", corpus_version)
    print()

    retrieval_cache = SimpleCache()
    response_cache = SimpleCache()

    query = "What are cats known for?"
    filters = {}

    print("Ask 1")
    ask(query, docs, filters, retrieval_cache, response_cache)

    print("Ask 2")
    ask(query, docs, filters, retrieval_cache, response_cache)


if __name__ == "__main__":

    run("Docs-Version1")

    run("Docs-Version2")