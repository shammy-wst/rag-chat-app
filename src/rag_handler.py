from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.chains import ConversationalRetrievalChain
import os

class RAGHandler:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.embeddings = OllamaEmbeddings(
            model=model_name
        )
        self.llm = OllamaLLM(
            model=model_name,
            num_ctx=2048
        )
        self.vector_store = None
        self.chain = None

    def process_pdfs(self, pdf_paths):
        """Traite les PDFs et crée la base de connaissances"""
        documents = []
        
        # Chargement des PDFs
        for pdf_path in pdf_paths:
            if os.path.exists(pdf_path):
                loader = PyPDFLoader(pdf_path)
                documents.extend(loader.load())

        # Découpage du texte en chunks plus petits
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.split_documents(documents)

        # Création de la base vectorielle
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings
        )

        # Initialisation de la chaîne de conversation
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 2}
            ),
            return_source_documents=True
        )

    def get_response(self, question, chat_history=[]):
        """Obtient une r��ponse à partir de la question et de l'historique"""
        if not self.chain:
            return "Veuillez d'abord charger des PDFs pour que je puisse répondre à vos questions."
        
        try:
            result = self.chain({"question": question, "chat_history": chat_history})
            return {
                "answer": result["answer"],
                "sources": [doc.metadata for doc in result["source_documents"]]
            }
        except Exception as e:
            return f"Erreur lors de la génération de la réponse: {str(e)}"
