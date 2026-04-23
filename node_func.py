from vector_store import RAGPipeline
from typing import List
from tool_retriever import get_tools
import logging
logging.basicConfig(level=logging.INFO)


def tool_node(state):
    """Performs the tool call"""
    tools = get_tools()
    tool_by_name = {tool.name: tool for tool in tools}
    logging.info(f"Tool called: {state.tool_calls[0]["name"]}")
    for tool_call in state.tool_calls:
        tool = tool_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])


    return observation

def store_node(state: List[dict]):
    """
    convert list of documents into embeddings and store them in the database
    """
    queries = [item['query'] for item in state]
    LIST_DOCUMENTS = [doc for item in state for doc in item['documents']]
    vectorstore = RAGPipeline.store(LIST_DOCUMENTS)
    retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 10, "fetch_k": 20}
)
    results = []
    for q in queries:
        docs = retriever.invoke(q)
        content = [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "")
        }
        for i, doc in enumerate(docs, 1)
    ]
        results.append({'query': q, 'context': content})

    return results

def summarize_per_query(results, llm):
    summaries = []

    for item in results:
        query = item["query"]
        context = item["context"]

        # format context
        context_text = "\n\n".join(
            [f"[{i+1}] {c['content']}\nSource: {c['source']}"
             for i, c in enumerate(context)]
        )

        prompt = f"""
You are a research assistant.

Answer the query using ONLY the provided context.

Instructions:
- Provide a clear summary
- If the results are insufficient, clearly say so.
- Ignore any citations like [1], [2] present in the context
- These are from original documents and may be incorrect
- Use ONLY the source URLs provided
- Do NOT copy citation numbers from the context
- At the end, list references with source URLs

Query:
{query}

Context:
{context_text}

Answer:
"""

        response = llm.invoke(prompt)

        summaries.append({
            "query": query,
            "answer": response.content,
            "sources": [c["source"] for c in context]
        })

    return summaries

def final_synthesis(parent_query,summaries, llm):

    combined_text = "\n\n".join(
        [f"Sub-query: {s['query']}\n{s['answer']}" for s in summaries]
    )

    prompt = f"""
You are an expert researcher.

The main user/research/search question is:
"{parent_query}"

You are given answers to multiple sub-queries that were used to explore this main question.

Your task:
- Synthesize all sub-query answers into a single coherent and structured report
- Directly answer the main research question
- Remove redundancy
- Merge overlapping insights
- Highlight key findings clearly
- Ensure logical flow (not just concatenation)
- At the end, list references with source URLs

Sub - query Context:
{combined_text}

Final Report (well-structured, with headings and references):
"""

    final_response = llm.invoke(prompt)

    return final_response.content
