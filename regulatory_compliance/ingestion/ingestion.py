import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from regulatory_compliance.core.config import settings
 
 
class PDFIngestion:
    """
    Handles PDF loading, cleaning and chunking.
    """
 
    def __init__(self):
 
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder
        (
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )
 
    def ingest(self, pdf_path: str) -> list[Document]:
        """
        Complete ingestion pipeline.
        """
 
        path = Path(pdf_path)
 
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
 
        # Load PDF
        loader = PyPDFLoader(str(path))
        documents = loader.load()
 
        # Clean text
        cleaned_documents = self.clean_documents(documents)
 
        # Add metadata
        enriched_documents = self.add_metadata(cleaned_documents, path.name)
 
        # Split into chunks
        chunks = self.split_documents(enriched_documents)
        return chunks
 
    def clean_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Clean extracted text.
        """
 
        cleaned = []
 
        for document in documents:
 
            text = document.page_content
 
            # # Remove excessive whitespace
            # text = re.sub(r"\s+", " ", text)
 
            # # Remove non-printable characters
            # text = re.sub(r"[^\x20-\x7E]+", " ", text)
 
            document.page_content = text.strip()
 
            cleaned.append(document)
 
        return cleaned
 
    def add_metadata(
        self,
        documents: list[Document],
        file_name: str,
    ) -> list[Document]:
        """
        Preserve metadata for future retrieval.
        """
 
        for document in documents:
 
            document.metadata["source"] = file_name
            document.metadata.setdefault("page", 0)
            document.metadata["section_number"] = None
            document.metadata["regulation_type"] = None
 
        return documents
 
    def split_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:
        """
        Split documents into chunks.
        """
 
        return self.splitter.split_documents(documents)
