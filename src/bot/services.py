from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings # Vector Embedding Technique
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS #VectorStore DB
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

class BotServices:
    
    def __init__(self, groq_api_key, google_api_key, embedding_model="models/embedding-001", llm_model="mixtral-8x7b-32768"):
        
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        
        self.prompt = ChatPromptTemplate.from_template("""
            Answer the questions based on the provided context only.
            Do not over use the word 'context'
            Do not say according to context instead use 'According to company policy' 
            If question is outside of context respond with "Sorry, I cannot help with this question."
            <context>{context}</context>
            Questions: {input}
        """)
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model, google_api_key=google_api_key)
    
    def generate_vector_store(self, pdf_dir='src/PDF'):
        loader = PyPDFDirectoryLoader(pdf_dir)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        final_document = text_splitter.split_documents(docs)
        vectors = FAISS.from_documents(final_document, self.embeddings)
        return vectors
    
    def save_vectors(self, vector_store, path):
        vector_store.save_local(path)
        
    def load_vector_store(self, path):
        return FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
    
    def get_answer(self, question, vector_store):
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        retriever = vector_store.as_retriever()
        retriever_chain = create_retrieval_chain(retriever, document_chain)
        response = retriever_chain.invoke({'input': question})
        return response['answer']