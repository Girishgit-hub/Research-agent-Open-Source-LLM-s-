import streamlit as st
import time
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Import your modules
from llm import llm_node, llm_reasoning_node
from node_func import tool_node, store_node, summarize_per_query, final_synthesis
from Rag_agent import rag_answer


# ---------------- CACHE MODELS (IMPORTANT) ----------------
@st.cache_resource
def get_llm():
    return llm_node()

@st.cache_resource
def get_reasoning_llm():
    return llm_reasoning_node()


# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Biomedical RAG", layout="wide")

st.title("🧬 BioEnergy RAG Assistant")
st.caption("PubMed + LLM + RAG pipeline")

# Sidebar
debug_mode = st.sidebar.checkbox("Show Debug Info")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
query = st.chat_input("Ask a biomedical question...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Running RAG pipeline... ⏳"):
            start = time.time()

            if debug_mode:
                answer, tool_results, summaries = rag_answer(query, debug=True)
            else:
                answer = rag_answer(query)

            end = time.time()

        st.markdown(answer)
        st.caption(f"⏱ Time: {round(end - start, 2)} sec")

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        # Debug info
        if debug_mode:
            with st.expander("🔬 Debug Info"):
                st.subheader("Tool Results")
                st.write(tool_results)

                st.subheader("Summaries")
                st.write(summaries)