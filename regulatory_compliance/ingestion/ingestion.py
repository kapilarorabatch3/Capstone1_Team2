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

        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
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

        path = Path(pdf_path)

        if not path.exists():

            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        loader = PyPDFLoader(str(path))

        documents = loader.load()

        cleaned_documents = self.clean_documents(documents)

        enriched_documents = self.add_metadata(cleaned_documents, path.name)

        chunks = self.split_documents(enriched_documents)

        print("Total chunks created:", len(chunks))

        return chunks

    def clean_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:

        cleaned = []

        for document in documents:

            document.page_content = document.page_content.strip()

            cleaned.append(document)

        return cleaned

    def add_metadata(
        self,
        documents: list[Document],
        file_name: str,
    ) -> list[Document]:

        for document in documents:

            page_number = document.metadata.get("page", 0)

            document.metadata.update(
                {
                    "file_name": file_name,
                    "page_number": page_number + 1,
                    "section_number": self.extract_section(document.page_content),
                    "regulation_type": self.detect_regulation_type(file_name),
                }
            )

        return documents

    def split_documents(
        self,
        documents: list[Document],
    ) -> list[Document]:

        return self.splitter.split_documents(documents)
