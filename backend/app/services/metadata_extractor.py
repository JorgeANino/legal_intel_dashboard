"""
Metadata extraction service with LLM integration and rule-based fallback
"""
import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import settings
from app.schemas.document import ExtractedMetadata


class MetadataExtractor:
    """Extract structured metadata from legal documents using LLM"""
    
    def __init__(self):
        # Initialize LLM (can use OpenAI or Anthropic)
        self.llm = None
        
        if settings.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=settings.OPENAI_API_KEY
                )
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
        elif settings.ANTHROPIC_API_KEY:
            try:
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0,
                    api_key=settings.ANTHROPIC_API_KEY
                )
            except Exception as e:
                print(f"Failed to initialize Anthropic: {e}")
    
    async def extract_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from document text
        
        Args:
            text: Full document text
            filename: Document filename for context
            
        Returns:
            Dictionary containing extracted metadata
        """
        if self.llm:
            return await self._extract_with_llm(text, filename)
        else:
            return self._extract_with_rules(text, filename)
    
    async def _extract_with_llm(self, text: str, filename: str) -> Dict[str, Any]:
        """Extract metadata using LLM with structured output"""
        
        # Truncate text if too long (keep first 8000 chars)
        truncated_text = text[:8000] if len(text) > 8000 else text
        
        # Create parser with our Pydantic model
        parser = PydanticOutputParser(pydantic_object=ExtractedMetadata)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal document analysis expert. Extract structured metadata from the provided legal document.

{format_instructions}

Be precise and only extract information explicitly stated in the document.
For dates, use YYYY-MM-DD format.
For contract_value, extract numeric value only (no currency symbols).
Set confidence_score between 0.0 and 1.0 based on how certain you are about the extraction."""),
            ("human", "Filename: {filename}\n\nDocument text:\n{text}\n\nExtract metadata:")
        ])
        
        # Create chain with parser
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({
                "filename": filename,
                "text": truncated_text,
                "format_instructions": parser.get_format_instructions()
            })
            
            # Convert Pydantic model to dict
            return result.model_dump()
            
        except Exception as e:
            print(f"LLM extraction error: {e}")
            # Fallback to rule-based
            return self._extract_with_rules(text, filename)
    
    def _extract_with_rules(self, text: str, filename: str) -> Dict[str, Any]:
        """Rule-based metadata extraction (fallback/mock)"""
        
        metadata = {
            "agreement_type": None,
            "governing_law": None,
            "jurisdiction": None,
            "geography": None,
            "industry": None,
            "parties": [],
            "effective_date": None,
            "expiration_date": None,
            "contract_value": None,
            "currency": None,
            "key_terms": {},
            "confidence_score": 0.5
        }
        
        # Agreement type patterns
        agreement_patterns = {
            "NDA": r'\b(non[-\s]disclosure|confidentiality)\s+agreement\b',
            "MSA": r'\bmaster\s+services?\s+agreement\b',
            "Franchise Agreement": r'\bfranchise\s+agreement\b',
            "Service Agreement": r'\bservice\s+agreement\b',
            "License Agreement": r'\blicense\s+agreement\b',
            "Employment Agreement": r'\bemployment\s+agreement\b',
            "Lease Agreement": r'\blease\s+agreement\b',
        }
        
        for agreement_type, pattern in agreement_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                metadata["agreement_type"] = agreement_type
                break
        
        # Governing law patterns
        law_patterns = {
            "UAE": r'\b(UAE|United Arab Emirates|Dubai|Abu Dhabi)\s+law\b',
            "UK": r'\b(UK|United Kingdom|English)\s+law\b',
            "Delaware": r'\bDelaware\s+law\b',
            "New York": r'\bNew York\s+law\b',
            "California": r'\bCalifornia\s+law\b',
        }
        
        for jurisdiction, pattern in law_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                metadata["governing_law"] = jurisdiction
                metadata["jurisdiction"] = jurisdiction
                break
        
        # Industry patterns
        industry_patterns = {
            "Technology": r'\b(software|technology|IT|SaaS|cloud|digital)\b',
            "Oil & Gas": r'\b(oil|gas|petroleum|energy|drilling)\b',
            "Healthcare": r'\b(healthcare|medical|pharmaceutical|hospital)\b',
            "Finance": r'\b(finance|banking|investment|securities)\b',
            "Real Estate": r'\b(real estate|property|lease|rental)\b',
        }
        
        for industry, pattern in industry_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                metadata["industry"] = industry
                break
        
        # Geography (simple heuristic)
        if metadata["governing_law"] in ["UAE"]:
            metadata["geography"] = "Middle East"
        elif metadata["governing_law"] in ["UK"]:
            metadata["geography"] = "Europe"
        elif metadata["governing_law"] in ["Delaware", "New York", "California"]:
            metadata["geography"] = "North America"
        
        # Extract dates (simple pattern)
        date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b'
        dates = re.findall(date_pattern, text)
        if dates:
            # First date is often effective date
            metadata["effective_date"] = dates[0]
        
        return metadata

