from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

loader = PyPDFLoader("my_resume.pdf")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# query = "What is my work experience?"
# results = retriever.invoke(query)

# print("--- TEST RESULT ---")
# print(results[0].page_content)