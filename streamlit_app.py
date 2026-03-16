import streamlit as st
import os
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import time

# --- CONFIGURATION & SECRETS ---
# For Streamlit Cloud, secrets are managed in the dashboard
# For local, it uses st.secrets (which reads from .streamlit/secrets.toml)
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# --- RAG ENGINE INTEGRATION ---
class RAGEngine:
    def __init__(self):
        self.persist_directory = "chroma_db"
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_store = self._initialize_vector_store()

    def _initialize_vector_store(self):
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )

    def retrieve_context(self, query: str, context_type: str = None):
        if context_type and context_type != "general":
            results = self.vector_store.similarity_search(query, k=3, filter={"type": {"$eq": context_type}})
        else:
            results = self.vector_store.similarity_search(query, k=3)
        return results

    def classify_intent(self, query: str):
        query_lower = query.lower()
        if any(kw in query_lower for kw in ["wattmonk", "services", "company", "ankit", "sheoran"]):
            return "wattmonk"
        elif any(kw in query_lower for kw in ["nec", "code", "article 690", "regulation", "standard", "rsd"]):
            return "nec"
        else:
            return "general"

# Initialize Engine
@st.cache_resource
def get_engine():
    return RAGEngine()

engine = get_engine()
gen_model = genai.GenerativeModel('gemini-flash-latest')

# --- STREAMLIT UI ---
st.set_page_config(page_title="RAG Solar Assistant", page_icon="☀️", layout="wide")

st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .source-tag { background-color: #1e293b; color: #38bdf8; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-right: 5px; }
    .intent-tag { font-weight: bold; text-transform: uppercase; font-size: 0.7rem; padding: 2px 5px; border-radius: 3px; }
    .intent-nec { color: #facc15; border: 1px solid #facc15; }
    .intent-wattmonk { color: #4ade80; border: 1px solid #4ade80; }
    .intent-general { color: #94a3b8; border: 1px solid #94a3b8; }
</style>
""", unsafe_allow_html=True)

st.title("☀️ RAG Solar Assistant")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            sources_html = ' '.join([f'<span class="source-tag">{s}</span>' for s in message["sources"]])
            st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)

if prompt := st.chat_input("Ask about Wattmonk or NEC Code..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Searching knowledge base...")
        
        intent = engine.classify_intent(prompt)
        context_docs = engine.retrieve_context(prompt, context_type=intent)
        sources = [doc.metadata.get("source", "Unknown") for doc in context_docs] if intent != "general" else []
        context_text = "\n\n".join([doc.page_content for doc in context_docs]) if intent != "general" else ""
        
        if intent == "general":
            final_prompt = f"User: {prompt}\nAssistant:"
        else:
            final_prompt = f"Context:\n{context_text}\n\nUser: {prompt}\nUse the context to answer. If not there, say so."

        try:
            response = gen_model.generate_content(final_prompt)
            full_response = response.text
            
            # Streaming effect
            displayed_text = ""
            for chunk in full_response.split():
                displayed_text += chunk + " "
                message_placeholder.markdown(displayed_text + "▌")
                time.sleep(0.02)
            message_placeholder.markdown(displayed_text)
            
            if sources:
                sources_html = ' '.join([f'<span class="source-tag">{s}</span>' for s in set(sources)])
                st.markdown(f"**Sources:** {sources_html}", unsafe_allow_html=True)
            
            intent_class = f"intent-{intent}"
            st.markdown(f"<span class='intent-tag {intent_class}'>{intent}</span>", unsafe_allow_html=True)

            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "sources": list(set(sources)),
                "intent": intent
            })
        except Exception as e:
            st.error(f"Error: {e}")
