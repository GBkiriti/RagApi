from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import logging as logger
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate
import os
import requests
from langchain.schema import Document 
app = FastAPI()

class Query(BaseModel):
    question: str

# Set the base URL for Ollama using localhost since it's in the same container
# OLLAMA_HOST = "http://localhost:11434"
OLLAMA_HOST =  "http://ollama:11434/"
cached_llm = Ollama(model="llama3.1",base_url=f"{OLLAMA_HOST}", temperature=0)

# Initialize Ollama embeddings and vector store
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
documents = ["FastAPI is a modern web framework.", "Chroma is an open-source vector database."]
folder_path = "chroma_db"

# Initialize vector store
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Initialize the Chroma vector store with the new import
vector_store = Chroma(persist_directory=folder_path, embedding_function=embedding)

raw_prompt = PromptTemplate.from_template(
    """ 
    <s>[INST] You are a technical assistant good at searching documents. 
    If you do not have an answer from the provided information, say so. 
    [/INST] </s>
    [INST] {input}
           Context: {context}
           Answer:
    [/INST]
    """
)
@app.get("/")
def home():
    return {"message": "API is running"}

@app.post('/embedToModel')
def embed_to_model(file_path: str, force: bool = False):
    """
    Endpoint to embed content from a file into the vector store.
    """
    try:
        # Step 1: Check if embedding already exists for the given CostalData
        existing_docs = vector_store.get(
            where={"CostalData": file_path},
            include=["documents", "metadatas"]
        )
        existing_ids = existing_docs.get("ids", [])
        
        # If embeddings exist and force is not set, skip embedding
        if existing_docs and not force and existing_ids:
            return {"message": f"Data for '{file_path}' is already embedded."}
        
        # If force=True, delete existing documents
        if force and existing_ids:
            vector_store.delete(ids=existing_ids)

        # Step 2: Read the file content
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
        
        # Step 3: Prepare content for embedding
        document = Document(
            page_content=file_content,
            metadata={"CostalData": file_path}
        )
        
        # Step 4: Add document to ChromaDB
        vector_store.add_documents([document])

        return {"message": f"Data from '{file_path}' has been successfully embedded."}

    except Exception as e:
        logger.error(f"Error while embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@app.post('/askEmbeddedModel')
def ask_embedded_model(query: str, file_path: str):
    """
    Endpoint to query the embedded data based on CostalData metadata.
    """
    try:
        # Step 1: Check if embeddings exist for the given CostalData
        existing_docs = vector_store.get(
            where={"CostalData": file_path},
            include=["documents", "metadatas"]
        )
        
        existing_ids = existing_docs.get("ids", [])
        if not existing_ids:
            raise HTTPException(status_code=404, detail=f"No embeddings found for file: {file_path}")

        # Step 2: Create a retriever to fetch documents by similarity
        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10, "filter": {"CostalData": file_path}}
        )

        # Step 3: Retrieve relevant documents using the query
        document_chain = create_stuff_documents_chain(cached_llm, raw_prompt)
        chain = create_retrieval_chain(retriever, document_chain)

        # Step 4: Invoke the chain with the user query
        result = chain.invoke({"input": query})

        # Step 5: Extract context and sources
        sources = []
        if 'context' in result:
            for doc in result["context"]:
                if doc.metadata.get("CostalData") == file_path:
                    sources.append({
                        "source": doc.metadata.get("CostalData"),
                        "page_content": doc.page_content
                    })

        response_answer = {
            "answer": result.get("answer", "No answer available"),
            "sources": sources
        }
        return response_answer

    except Exception as e:
        logger.error(f"Error while querying model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model query failed: {str(e)}")
    
@app.post('/askModel')
def ask_embedded_model(query: str):
    """
    Endpoint to ask a question using the Ollama LLM.
    """
    try:
        # Construct the raw prompt using PromptTemplate
        raw_prompt_template = PromptTemplate.from_template(
            """
            <s>[INST] You are a technical assistant good at answering the queries asked to you.
            [/INST] </s>
            [INST] {input}
                Context: "You are an AI Assistant, known for better and concise responses for the given query."
                Answer:
            [/INST]
            """
        )
        
        # Render the prompt to a string by formatting it with the query
        raw_prompt = raw_prompt_template.format(input=query)
        
        # Invoke the LLM using the formatted raw_prompt
        response = cached_llm.invoke(
            input=raw_prompt,
            stream=False,
            model='llama3.1'
        )
        
        # Ensure response is in the expected format and return it
        if not response:
            raise HTTPException(status_code=500, detail="No response from the LLM")

        return response

    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(status_code=500, detail=f"Error invoking LLM: {str(e)}")
@app.get('/AskModel')
def askModel(prompt: str):
    res = requests.post('http://ollama:11434/api/generate', json={
        "prompt": prompt,
        "stream": False,
        "model": 'llama3.1'
    })
    return Response(res.response, media_type="application/json")