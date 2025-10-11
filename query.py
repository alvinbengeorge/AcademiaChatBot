from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from generate_chroma import CHROMA_LOC, get_embedding_functions
import glob
import json

EMBEDDING_FUNCTION = get_embedding_functions()
db = Chroma(
    embedding_function=EMBEDDING_FUNCTION,
    persist_directory=CHROMA_LOC
)

TEMPLATE = """
This is the database of a SINGLE STUDENT and his subjects, attendance, marks, timetable and other academic information.
You have to sort through this and find the answer to the question asked. You must only answer based on the context provided.
You should answer in a concise manner. 

Answer the question based on the following context:
{context}

Some things that are to be noted:
- The context data contains slots and timings, and those slots can be correlated with the timetable data to find out which subject is at what time.
- The attendance data contains hours absent, total classes and attendance percentage for each subject.
- The marks data contains test names and scores for each subject. You can calculate the total marks from it

------------------------------------
Answer the question based on the above context:
{question}
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_template(TEMPLATE)


def query(text: str):
    results = db.similarity_search_with_score(text, k=8)
    # results = sorted(results, key=lambda x: x[1], reverse=True)
    context = "\n------\n".join([doc.metadata['source'] + "\n" + doc.page_content for doc, _ in results])

    prompt = PROMPT_TEMPLATE.format(context=context, question=text)
    model = OllamaLLM(model="llama3.2:1b")    
    print(context)
    # print(*results, sep="\n")
    response = model.invoke(prompt)
    print(response)

while True:
    text = input("Enter query: ")
    query(text)
