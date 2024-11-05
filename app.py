from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

app = FastAPI()

class Query(BaseModel):
    question: str

# Initialize Ollama embeddings
embeddings = OllamaEmbeddings()

# Load documents and create Chroma vector store
documents = ["Your documents here"]
vector_store = Chroma.from_documents(documents, embeddings)

# Initialize RetrievalQA chain
retriever = vector_store.as_retriever()
qa_chain = RetrievalQA(retriever=retriever, llm=OpenAI())

@app.post("/query")
async def query(data: Query):
    try:
        answer = qa_chain.run(data.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))