"""
Query service for natural language querying across documents
"""
from typing import List, Dict, Any
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.models.document import Document, DocumentMetadata, Query
from app.core.config import settings


class QueryService:
    """Service for natural language querying across documents"""
    
    def __init__(self):
        # Initialize LLM
        self.llm = None
        
        if settings.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=settings.OPENAI_API_KEY
                )
            except:
                pass
        elif settings.ANTHROPIC_API_KEY:
            try:
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0,
                    api_key=settings.ANTHROPIC_API_KEY
                )
            except:
                pass

    async def execute_query(
        self,
        question: str,
        user_id: int,
        db: AsyncSession,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """Execute natural language query against documents"""
        start_time = time.time()
        
        # Step 1: Analyze query to determine what metadata fields are needed
        query_analysis = await self._analyze_query(question)
        
        # Step 2: Build and execute database query
        results = await self._fetch_matching_documents(
            query_analysis,
            user_id,
            db,
            max_results
        )
        
        # Step 3: Format results
        formatted_results = self._format_results(results, query_analysis)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Step 4: Log query
        query_record = Query(
            user_id=user_id,
            query_text=question,
            query_type="interrogation",
            results={"count": len(formatted_results)},
            execution_time_ms=execution_time_ms
        )
        db.add(query_record)
        await db.commit()
        
        return {
            "question": question,
            "results": formatted_results,
            "total_results": len(formatted_results),
            "execution_time_ms": execution_time_ms
        }
    
    async def _analyze_query(self, question: str) -> Dict[str, Any]:
        """Analyze query to determine intent and required fields"""
        
        if not self.llm:
            return self._rule_based_analysis(question)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the user's question about legal documents and determine:
1. What metadata fields are needed (agreement_type, governing_law, jurisdiction, industry, etc.)
2. What filters to apply
3. What fields to return in results

Return JSON with:
- fields_needed: array of metadata field names
- filters: object with field names and required values
- return_fields: array of fields to include in response

Examples:
Q: "Which agreements are governed by UAE law?"
A: {"fields_needed": ["governing_law"], "filters": {"governing_law": "UAE"}, "return_fields": ["document", "governing_law"]}

Q: "Show me all NDAs"
A: {"fields_needed": ["agreement_type"], "filters": {"agreement_type": "NDA"}, "return_fields": ["document", "agreement_type", "governing_law"]}"""),
            ("human", "Question: {question}")
        ])
        
        parser = JsonOutputParser()
        chain = prompt | self.llm | parser
        
        try:
            result = await chain.ainvoke({"question": question})
            return result
        except:
            return self._rule_based_analysis(question)
    
    def _rule_based_analysis(self, question: str) -> Dict[str, Any]:
        """Simple rule-based query analysis"""
        question_lower = question.lower()
        
        analysis = {
            "fields_needed": [],
            "filters": {},
            "return_fields": ["document", "agreement_type", "governing_law"]
        }
        
        # Check for governing law mentions
        if "uae" in question_lower or "dubai" in question_lower:
            analysis["fields_needed"].append("governing_law")
            analysis["filters"]["governing_law"] = "UAE"
        elif "uk" in question_lower or "english" in question_lower:
            analysis["fields_needed"].append("governing_law")
            analysis["filters"]["governing_law"] = "UK"
        
        # Check for agreement type mentions
        if "nda" in question_lower or "non-disclosure" in question_lower:
            analysis["fields_needed"].append("agreement_type")
            analysis["filters"]["agreement_type"] = "NDA"
        elif "msa" in question_lower or "master service" in question_lower:
            analysis["fields_needed"].append("agreement_type")
            analysis["filters"]["agreement_type"] = "MSA"
        
        # Check for industry mentions
        if "oil" in question_lower or "gas" in question_lower:
            analysis["fields_needed"].append("industry")
            analysis["filters"]["industry"] = "Oil & Gas"
        elif "technology" in question_lower or "tech" in question_lower:
            analysis["fields_needed"].append("industry")
            analysis["filters"]["industry"] = "Technology"
        
        return analysis
    
    async def _fetch_matching_documents(
        self,
        query_analysis: Dict[str, Any],
        user_id: int,
        db: AsyncSession,
        max_results: int
    ) -> List[Document]:
        """Fetch documents matching the query criteria"""
        
        # Build query
        stmt = select(Document).options(
            selectinload(Document.doc_metadata)
        ).where(
            and_(
                Document.user_id == user_id,
                Document.processed == True
            )
        )
        
        # Apply filters from query analysis
        filters = query_analysis.get("filters", {})
        if filters:
            # Join with metadata table
            stmt = stmt.join(DocumentMetadata)
            
            for field, value in filters.items():
                if field == "agreement_type":
                    stmt = stmt.where(DocumentMetadata.agreement_type == value)
                elif field == "governing_law":
                    stmt = stmt.where(DocumentMetadata.governing_law == value)
                elif field == "jurisdiction":
                    stmt = stmt.where(DocumentMetadata.jurisdiction == value)
                elif field == "industry":
                    stmt = stmt.where(DocumentMetadata.industry == value)
        
        stmt = stmt.limit(max_results)
        
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    def _format_results(
        self,
        documents: List[Document],
        query_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format documents into response structure"""
        
        return_fields = query_analysis.get("return_fields", [])
        results = []
        
        for doc in documents:
            result = {
                "document": doc.filename,
                "document_id": doc.id
            }
            
            if doc.doc_metadata:
                metadata_dict = {}
                
                if not return_fields or "agreement_type" in return_fields:
                    metadata_dict["agreement_type"] = doc.doc_metadata.agreement_type
                
                if not return_fields or "governing_law" in return_fields:
                    metadata_dict["governing_law"] = doc.doc_metadata.governing_law
                
                if not return_fields or "jurisdiction" in return_fields:
                    metadata_dict["jurisdiction"] = doc.doc_metadata.jurisdiction
                
                if not return_fields or "industry" in return_fields:
                    metadata_dict["industry"] = doc.doc_metadata.industry
                
                if not return_fields or "geography" in return_fields:
                    metadata_dict["geography"] = doc.doc_metadata.geography
                
                result["metadata"] = metadata_dict
            
            results.append(result)
        
        return results

