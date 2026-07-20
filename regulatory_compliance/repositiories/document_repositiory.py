import json
import logging
import uuid
from typing import List
from langchain_core.documents import Document
from regulatory_compliance.core.db import Database
 
# logger
logger = logging.getLogger(__name__)
 
 
class DocumentRepository:
    """
    Repository class responsible for all database operations
    related to regulatory documents.
    """
 
    def insert_document(
        self,
        document_name: str,
        regulation_type: str,
        source_date,
        version: str,
        total_pages: int,
        total_chunks: int,
    ) -> str:
        document_id = str(uuid.uuid4())
 
        sql = """
        INSERT INTO documents
        (
            id,
            document_name,
            regulation_type,
            source_date,
            version,
            total_pages,
            total_chunks
        )
 
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s
        )
        """
 
        try:
 
            with Database.get_connection() as conn:
 
                with conn.cursor() as cur:
 
                    cur.execute(
                        sql,
                        (
                            document_id,
                            document_name,
                            regulation_type,
                            source_date,
                            version,
                            total_pages,
                            total_chunks,
                        ),
                    )
 
                conn.commit()
 
            logger.info("Document inserted successfully.")
 
            return document_id
 
        except Exception as ex:
 
            logger.exception("Failed to insert document.")
 
            raise ex
 
    def insert_chunks(
        self,
        document_id: str,
        chunks: List[Document],
    ):
        sql = """
        INSERT INTO document_chunks
        (
            id,
            document_id,
            chunk_index,
            page_number,
            content,
            metadata
        )
 
        VALUES
        (
            %s,%s,%s,%s,%s,%s
        )
        """
 
        try:
 
            with Database.get_connection() as conn:
 
                with conn.cursor() as cur:
 
                    for index, chunk in enumerate(chunks):
 
                        chunk_id = str(uuid.uuid4())
 
                        page_number = chunk.metadata.get("page", 0)
 
                        metadata = json.dumps(chunk.metadata)
 
                        cur.execute(
                            sql,
                            (
                                chunk_id,
                                document_id,
                                index,
                                page_number,
                                chunk.page_content,
                                metadata,
                            ),
                        )
 
                conn.commit()
 
            logger.info(
                "%s chunks inserted successfully.",
                len(chunks),
            )
 
        except Exception as ex:
 
            logger.exception("Chunk insertion failed.")
 
            raise ex