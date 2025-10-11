import os
import shutil
import json
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from typing import List

CHROMA_LOC = "chroma_structured/"

def load_data():
    """Load JSON files from structured_data folder"""
    loader = DirectoryLoader(
        "./structured_data/", 
        glob="**/*.json", 
        loader_cls=JSONLoader, 
        loader_kwargs={'jq_schema': '.[]', 'text_content': False}
    )
    docs = loader.load()
    return docs

def split_document(doc: List[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=80,
        length_function=len
    )
    return text_splitter.split_documents(doc)

def get_embedding_functions():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings

def calculate_chunk_ids(chunks: List[Document]) -> List[Document]:
    # Assign unique, sequential chunk IDs per source file, skip if source is None
    page_chunk_counts = {}
    for chunk in chunks:
        source = chunk.metadata.get("source")
        if not source:
            continue  # Skip chunks with None or empty source
        if source not in page_chunk_counts:
            page_chunk_counts[source] = 0
        chunk_index = page_chunk_counts[source]
        chunk_id = f"{os.path.basename(source)}:{chunk_index}"
        chunk.metadata["id"] = chunk_id
        page_chunk_counts[source] += 1
    return chunks

def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_LOC, embedding_function=get_embedding_functions()
    )
    chunks_with_ids = calculate_chunk_ids(chunks)
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)


def clear_database():
    if os.path.exists(CHROMA_LOC):
        shutil.rmtree(CHROMA_LOC)

if __name__ == "__main__":
    clear_database()
    document = load_data()
    chunks = split_document(document)
    add_to_chroma(chunks)
