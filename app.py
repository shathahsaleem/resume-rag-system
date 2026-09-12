from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)


loader_sarah = PyPDFLoader("sarah_resume.pdf")
chunks_sarah = text_splitter.split_documents(loader_sarah.load())
for doc in chunks_sarah:
    doc.metadata["candidate_id"] = "sarah_123"


loader_alex = PyPDFLoader("alex_resume.pdf")
chunks_alex = text_splitter.split_documents(loader_alex.load())
for doc in chunks_alex:
    doc.metadata["candidate_id"] = "alex_456"

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma.from_documents(
    chunks_sarah + chunks_alex, 
    embeddings, 
    persist_directory="./chroma_db_test"
)

retriever = vectorstore.as_retriever(search_kwargs={
    "k": 4,
    "filter": {"candidate_id": "alex_456"}
})

llm = ChatGoogleGenerativeAI(model="models/gemini-3.6-flash")

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question based only on the following context: {context}"), 
    ("human", "Question: {question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

query = "What is Sarah's experience with Python?" # Result: No info about Sarah (because we filtered for Alex's resume!)
response = rag_chain.invoke(query)

print("\n--- TEST RESPONSE ---")
print(response)