import streamlit as st
from drive_handler import GoogleDriveHandler
from rag_handler import RAGHandler
import os

st.set_page_config(page_title="RAG Chat App", layout="wide")

def init_session_state():
    if 'drive_handler' not in st.session_state:
        st.session_state.drive_handler = GoogleDriveHandler()
    if 'rag_handler' not in st.session_state:
        st.session_state.rag_handler = RAGHandler()
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = []
    if 'selected_pdfs' not in st.session_state:
        st.session_state.selected_pdfs = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_pdfs' not in st.session_state:
        st.session_state.processed_pdfs = False

def main():
    st.title("RAG Chat Application")
    
    init_session_state()
    
    # Sidebar pour les contrôles
    with st.sidebar:
        st.header("Configuration")
        
        # Bouton pour rafraîchir la liste des PDFs
        if st.button("🔄 Rafraîchir les PDFs"):
            with st.spinner("Chargement des PDFs..."):
                st.session_state.pdf_files = st.session_state.drive_handler.list_pdfs()
        
        # Affichage et sélection des PDFs disponibles
        st.subheader("PDFs disponibles")
        if st.session_state.pdf_files:
            selected_pdfs = []
            for pdf in st.session_state.pdf_files:
                if st.checkbox(f"📄 {pdf['name']}", key=pdf['id']):
                    selected_pdfs.append(pdf)
            st.session_state.selected_pdfs = selected_pdfs
        else:
            st.info("Aucun PDF trouvé. Cliquez sur Rafraîchir pour chercher des PDFs.")

        if st.session_state.selected_pdfs:
            if st.button("📥 Télécharger et traiter les PDFs"):
                with st.spinner("Traitement en cours..."):
                    pdf_paths = []
                    for pdf in st.session_state.selected_pdfs:
                        output_path = f"data/{pdf['name']}"
                        os.makedirs("data", exist_ok=True)
                        success = st.session_state.drive_handler.download_pdf(pdf['id'], output_path)
                        if success:
                            pdf_paths.append(output_path)
                            st.success(f"✅ {pdf['name']} traité!")
                        else:
                            st.error(f"❌ Erreur lors du traitement de {pdf['name']}")
                    
                    if pdf_paths:
                        st.session_state.rag_handler.process_pdfs(pdf_paths)
                        st.session_state.processed_pdfs = True
                        st.success("🎉 Base de connaissances créée avec succès!")

    # Zone principale pour le chat
    st.header("💬 Chat")
    
    # Affichage de l'historique des messages
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Zone de saisie du message
    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        if not st.session_state.processed_pdfs:
            with st.chat_message("assistant"):
                st.write("⚠️ Veuillez d'abord charger et traiter des PDFs.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Réflexion en cours..."):
                    response = st.session_state.rag_handler.get_response(
                        prompt,
                        [(msg["role"], msg["content"]) for msg in st.session_state.chat_history[:-1]]
                    )
                    
                    if isinstance(response, dict):
                        st.write(response["answer"])
                        with st.expander("Sources"):
                            for source in response["sources"]:
                                st.write(f"📄 {source.get('source', 'Document inconnu')}")
                    else:
                        st.write(response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
