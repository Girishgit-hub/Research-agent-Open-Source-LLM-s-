import dotenv
dotenv.load_dotenv()
from llm import llm_node, llm_reasoning_node
from node_func import tool_node, store_node, summarize_per_query, final_synthesis


def rag_answer(user_query, debug=False):
    system_prompt = "You are a biomedical search query optimization expert."

    reasoning_llm = llm_reasoning_node()
    llm = llm_node()

    # Step 1: Query optimization
    response = reasoning_llm.invoke([
        ("system", system_prompt),
        ("human", user_query)
    ])

    # Step 2: Tool call (PubMed or tavilysearch etc.)
    tool_results = tool_node(response)

    # Step 3: Store / embed / retrieve
    relevant_context = store_node(tool_results)

    # Step 4: Summarize
    summaries = summarize_per_query(relevant_context, llm)

    # Step 5: Final synthesis
    result = final_synthesis(user_query,summaries, llm)

    if debug:
        return result, tool_results, summaries
    return result