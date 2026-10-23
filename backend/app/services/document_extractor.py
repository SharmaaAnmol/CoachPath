"""
Document Text Extraction Service for CoachPath.
Extracts clean, normalized text and page/section boundaries from PDF and DOCX resume documents.
Validates magic-byte signatures, detects encrypted files, and identifies image-only/scanned documents.
"""
from __future__ import annotations

import io
import logging
import re
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import pypdf
import docx

from app.core.exceptions import AppException
from app.schemas.resume import ParsingErrorCategory

logger = logging.getLogger(__name__)


class DocumentExtractionException(AppException):
    """Exception raised when document text extraction fails."""

    def __init__(
        self,
        message: str,
        category: str = ParsingErrorCategory.CORRUPTED_DOCUMENT,
        status_code: int = 400,
    ) -> None:
        super().__init__(
            status_code=status_code,
            code="DOCUMENT_EXTRACTION_ERROR",
            message=message,
        )
        self.category = category


@dataclass
class PageText:
    """Page-level text structure preserving document geometry."""
    page_number: int
    text: str
    char_count: int = 0

    def __post_init__(self) -> None:
        self.char_count = len(self.text)


@dataclass
class ExtractedDocumentText:
    """Consolidated representation of extracted document contents."""
    raw_text: str
    pages: List[PageText] = field(default_factory=list)
    total_pages: int = 1
    char_count: int = 0
    word_count: int = 0
    mime_type: str = "application/pdf"

    def __post_init__(self) -> None:
        self.char_count = len(self.raw_text)
        self.word_count = len(self.raw_text.split())


class DocumentExtractorService:
    """
    Validates document binary headers and extracts structured text contents.
    Decoupled from AI parsing logic.
    """

    PDF_MAGIC = b"%PDF-"
    ZIP_MAGIC = b"PK\x03\x04"

    PDF_MIME = "application/pdf"
    DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    MIN_TEXT_CHARS = 50

    def detect_format_and_validate(self, content: bytes, filename: str) -> Tuple[str, str]:
        """
        Validates both file extension and actual file header magic bytes.
        Returns verified (mime_type, extension).
        Raises DocumentExtractionException on invalid or spoofed files.
        """
        if not content or len(content) == 0:
            raise DocumentExtractionException(
                "Uploaded file is empty (0 bytes).",
                category=ParsingErrorCategory.EMPTY_DOCUMENT,
            )

        lower_name = filename.lower()
        has_pdf_ext = lower_name.endswith(".pdf")
        has_docx_ext = lower_name.endswith(".docx")

        if not (has_pdf_ext or has_docx_ext):
            raise DocumentExtractionException(
                f"Unsupported document format for '{filename}'. Only PDF (.pdf) and Word (.docx) files are supported.",
                category=ParsingErrorCategory.UNSUPPORTED_FORMAT,
            )

        # Inspect binary magic bytes
        if content.startswith(self.PDF_MAGIC):
            if not has_pdf_ext:
                raise DocumentExtractionException(
                    "File content is PDF, but filename extension does not match.",
                    category=ParsingErrorCategory.UNSUPPORTED_FORMAT,
                )
            return self.PDF_MIME, "pdf"

        elif content.startswith(self.ZIP_MAGIC):
            if not has_docx_ext:
                raise DocumentExtractionException(
                    "File content is ZIP archive, but filename extension is not .docx.",
                    category=ParsingErrorCategory.UNSUPPORTED_FORMAT,
                )
            # Verify DOCX internal XML structure
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    namelist = zf.namelist()
                    if not any("word/document.xml" in name for name in namelist):
                        raise DocumentExtractionException(
                            "ZIP archive does not contain a valid Word document structure.",
                            category=ParsingErrorCategory.CORRUPTED_DOCUMENT,
                        )
            except zipfile.BadZipFile as exc:
                raise DocumentExtractionException(
                    "Corrupt or malformed DOCX archive.",
                    category=ParsingErrorCategory.CORRUPTED_DOCUMENT,
                ) from exc
            return self.DOCX_MIME, "docx"

        else:
            raise DocumentExtractionException(
                "File contents do not match expected PDF or DOCX binary signature.",
                category=ParsingErrorCategory.UNSUPPORTED_FORMAT,
            )

    def extract_text(self, content: bytes, mime_type: str) -> ExtractedDocumentText:
        """
        Extracts clean, normalized text from document bytes.
        Preserves section/page boundaries.
        """
        if mime_type == self.PDF_MIME:
            return self._extract_pdf(content)
        elif mime_type == self.DOCX_MIME:
            return self._extract_docx(content)
        else:
            raise DocumentExtractionException(
                f"Cannot extract text from unsupported MIME type '{mime_type}'.",
                category=ParsingErrorCategory.UNSUPPORTED_FORMAT,
            )

    def _extract_pdf(self, content: bytes) -> ExtractedDocumentText:
        """Extracts text from PDF document using pypdf."""
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
        except Exception as exc:
            logger.error("pypdf failed to open PDF document: %s", exc)
            raise DocumentExtractionException(
                f"Failed to read PDF document: {exc}",
                category=ParsingErrorCategory.CORRUPTED_DOCUMENT,
            ) from exc

        if reader.is_encrypted:
            raise DocumentExtractionException(
                "Password-protected or encrypted PDF files are not supported.",
                category=ParsingErrorCategory.DOCUMENT_ENCRYPTED,
            )

        pages: List[PageText] = []
        raw_page_texts: List[str] = []

        try:
            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                clean_page = self._normalize_whitespace(page_text)
                pages.append(PageText(page_number=idx, text=clean_page))
                if clean_page:
                    raw_page_texts.append(f"--- Page {idx} ---\n{clean_page}")
        except Exception as exc:
            logger.error("Failed extracting text from PDF page: %s", exc)
            raise DocumentExtractionException(
                f"Error extracting text from PDF pages: {exc}",
                category=ParsingErrorCategory.CORRUPTED_DOCUMENT,
            ) from exc

        full_text = "\n\n".join(raw_page_texts).strip()

        # Check for empty or scanned image-only PDF
        if len(full_text.replace("--- Page", "").strip()) < self.MIN_TEXT_CHARS:
            raise DocumentExtractionException(
                "Insufficient text extracted from document. The PDF appears to be a scanned image and requires OCR to parse.",
                category=ParsingErrorCategory.INSUFFICIENT_TEXT_OCR_REQUIRED,
            )

        return ExtractedDocumentText(
            raw_text=full_text,
            pages=pages,
            total_pages=len(pages),
            mime_type=self.PDF_MIME,
        )

    def _extract_docx(self, content: bytes) -> ExtractedDocumentText:
        """Extracts text from DOCX document using python-docx."""
        try:
            doc = docx.Document(io.BytesIO(content))
        except Exception as exc:
            logger.error("python-docx failed to open document: %s", exc)
            raise DocumentExtractionException(
                f"Failed to read DOCX document: {exc}",
                category=ParsingErrorCategory.CORRUPTED_DOCUMENT,
            ) from exc

        paragraphs: List[str] = []

        # 1. Extract standard paragraphs
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)

        # 2. Extract tables (resumes often use tables for layout)
        for table in doc.tables:
            for row in table.rows:
                row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_texts:
                    # Join distinct cell texts with bullet separator
                    paragraphs.append(" | ".join(row_texts))

        full_text = self._normalize_whitespace("\n".join(paragraphs))

        if len(full_text.strip()) < self.MIN_TEXT_CHARS:
            raise DocumentExtractionException(
                "Document contains no readable text or is empty.",
                category=ParsingErrorCategory.EMPTY_DOCUMENT,
            )

        page_item = PageText(page_number=1, text=full_text)
        return ExtractedDocumentText(
            raw_text=full_text,
            pages=[page_item],
            total_pages=1,
            mime_type=self.DOCX_MIME,
        )

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalizes excessive whitespace while preserving line and paragraph breaks.
        Strips non-printable control characters.
        """
        if not text:
            return ""

        # Remove non-printable control characters (except newline, tab, carriage return)
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        # Normalize line endings to \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace excessive horizontal whitespace with a single space
        text = re.sub(r"[ \t]+", " ", text)

        # Replace 3 or more consecutive newlines with 2 newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()


# Singleton extractor service
document_extractor = DocumentExtractorService()
