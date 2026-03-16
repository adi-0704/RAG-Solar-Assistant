# Solar RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for answering queries about NEC code guidelines and Wattmonk company information.

## Project Structure
- `backend/`: FastAPI server and RAG engine.
- `frontend/`: Streamlit chat interface.
- `data/`: Knowledge base documents.

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key:**
   - Open `backend/.env`.
   - Replace `your_gemini_api_key_here` with your actual Google Gemini API Key.

3. **Initialize Knowledge Base:**
   Run the following command to index the project data:
   ```bash
   python backend/rag_engine.py
   ```

4. **Run the Application:**

   **Start the Backend (FastAPI):**
   ```bash
   uvicorn backend.main:app --reload
   ```

   **Start the Frontend (Streamlit):**
   ```bash
   streamlit run frontend/app.py
   ```

## Features
- **Multi-Context Handling:** Seamlessly switches between NEC, Wattmonk, and general queries.
- **Source Attribution:** Indicates where the information was retrieved from.
- **Intelligent Retrieval:** Uses ChromaDB for similarity search and Gemini for generation.
- **Premium UI:** Modern dark-themed chat interface.
