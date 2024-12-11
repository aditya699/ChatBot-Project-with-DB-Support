'''
Author -Aditya Bhatt  12:29PM 11-12-2024

Objective-
1.Function for a RAG tool

'''
import os
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

load_dotenv()
file_path = "../../company_policy.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print(len(docs))

print(docs[4].page_content[0:100])
print(docs[0].metadata)
os.environ["GOOGLE_API_KEY"] =os.getenv("GEMINI_API_KEY")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=500)
splits = text_splitter.split_documents(docs)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

retriever = vectorstore.as_retriever()


os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

llm = ChatAnthropic(model="claude-3-haiku-20240307",max_tokens=4092)


system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. "
    "\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

results = rag_chain.invoke({"input": "What is social media policy in my organisation?"})
print(results["context"][0].page_content)

