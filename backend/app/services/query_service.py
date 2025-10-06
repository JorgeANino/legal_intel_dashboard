"""
Query service for natural language querying across documents
"""
# Standard library imports
import contextlib
import time
from typing import Any

# Local application imports
from app.core.config import settings
from app.models.document import Document, DocumentMetadata, Query
# Third-party imports
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class QueryService:
    """Service for natural language querying across documents"""

    def __init__(self):
        # Initialize LLM
        self.llm = None

        if settings.OPENAI_API_KEY:
            with contextlib.suppress(Exception):
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini", temperature=0, api_key=settings.OPENAI_API_KEY
                )
        elif settings.ANTHROPIC_API_KEY:
            with contextlib.suppress(Exception):
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    temperature=0,
                    api_key=settings.ANTHROPIC_API_KEY,
                )

    async def execute_query(
        self, 
        question: str, 
        user_id: int, 
        db: AsyncSession, 
        max_results: int = 10,
        page: int = 1,
        filters: dict[str, Any] | None = None,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> dict[str, Any]:
        """Execute natural language query against documents"""
        start_time = time.time()

        # Step 1: Analyze query to determine what metadata fields are needed
        query_analysis = await self._analyze_query(question)

        # Step 2: Build and execute database query
        results, total_count = await self._fetch_matching_documents(
            query_analysis, user_id, db, max_results, page, filters, sort_by, sort_order
        )

        # Step 3: Format results
        formatted_results = self._format_results(results, query_analysis)

        execution_time_ms = int((time.time() - start_time) * 1000)
        total_pages = (total_count + max_results - 1) // max_results

        # Step 4: Log query
        query_record = Query(
            user_id=user_id,
            query_text=question,
            query_type="interrogation",
            results={"count": len(formatted_results)},
            execution_time_ms=execution_time_ms,
        )
        db.add(query_record)
        await db.commit()

        return {
            "question": question,
            "results": formatted_results,
            "total_results": total_count,
            "page": page,
            "per_page": max_results,
            "total_pages": total_pages,
            "execution_time_ms": execution_time_ms,
            "filters_applied": filters,
        }

    async def _analyze_query(self, question: str) -> dict[str, Any]:
        """Analyze query to determine intent and required fields"""

        if not self.llm:
            return self._rule_based_analysis(question)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Analyze the user's question about legal documents and determine:
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
A: {"fields_needed": ["agreement_type"], "filters": {"agreement_type": "NDA"}, "return_fields": ["document", "agreement_type", "governing_law"]}""",
                ),
                ("human", "Question: {question}"),
            ]
        )

        parser = JsonOutputParser()
        chain = prompt | self.llm | parser

        try:
            result = await chain.ainvoke({"question": question})
            return result
        except Exception:
            return self._rule_based_analysis(question)

    def _rule_based_analysis(self, question: str) -> dict[str, Any]:
        """Simple rule-based query analysis"""
        question_lower = question.lower()

        analysis = {
            "fields_needed": [],
            "filters": {},
            "return_fields": ["document", "agreement_type", "governing_law"],
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
        query_analysis: dict[str, Any], 
        user_id: int, 
        db: AsyncSession, 
        max_results: int,
        page: int = 1,
        filters: dict[str, Any] | None = None,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> tuple[list[Document], int]:
        """Fetch documents matching the query criteria"""

        # Build base query
        stmt = (
            select(Document)
            .options(selectinload(Document.doc_metadata))
            .where(and_(Document.user_id == user_id, Document.processed is True))
        )

        # Apply filters from query analysis
        analysis_filters = query_analysis.get("filters", {})
        if analysis_filters:
            # Join with metadata table
            stmt = stmt.join(DocumentMetadata)

            for field, value in analysis_filters.items():
                if field == "agreement_type":
                    stmt = stmt.where(DocumentMetadata.agreement_type == value)
                elif field == "governing_law":
                    stmt = stmt.where(DocumentMetadata.governing_law == value)
                elif field == "jurisdiction":
                    stmt = stmt.where(DocumentMetadata.jurisdiction == value)
                elif field == "industry":
                    stmt = stmt.where(DocumentMetadata.industry == value)

        # Apply additional filters
        if filters:
            if not analysis_filters:  # Only join if not already joined
                stmt = stmt.join(DocumentMetadata)
            
            if filters.get("agreement_types"):
                stmt = stmt.where(DocumentMetadata.agreement_type.in_(filters["agreement_types"]))
            if filters.get("jurisdictions"):
                stmt = stmt.where(DocumentMetadata.jurisdiction.in_(filters["jurisdictions"]))
            if filters.get("industries"):
                stmt = stmt.where(DocumentMetadata.industry.in_(filters["industries"]))
            if filters.get("geographies"):
                stmt = stmt.where(DocumentMetadata.geography.in_(filters["geographies"]))

        # Apply sorting
        if sort_by == "date":
            if sort_order == "asc":
                stmt = stmt.order_by(Document.upload_date.asc())
            else:
                stmt = stmt.order_by(Document.upload_date.desc())
        elif sort_by == "document_name":
            if sort_order == "asc":
                stmt = stmt.order_by(Document.filename.asc())
            else:
                stmt = stmt.order_by(Document.filename.desc())
        else:  # relevance - default
            stmt = stmt.order_by(Document.upload_date.desc())

        # Get total count for pagination
        count_stmt = select(func.count(Document.id)).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * max_results
        stmt = stmt.offset(offset).limit(max_results)

        result = await db.execute(stmt)
        return list(result.scalars().all()), total_count

    def _format_results(
        self, documents: list[Document], query_analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Format documents into response structure"""

        return_fields = query_analysis.get("return_fields", [])
        results = []

        for doc in documents:
            result = {"document": doc.filename, "document_id": doc.id}

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

    async def get_query_suggestions(self, query: str, limit: int, db: AsyncSession) -> dict[str, Any]:
        """
        Generate query suggestions based on:
        - Document metadata (agreement types, jurisdictions, industries)
        - Popular query patterns
        - Legal terminology
        """
        suggestions = []
        popular_queries = []
        legal_terms = []
        metadata_suggestions = {
            "agreement_types": [],
            "jurisdictions": [],
            "industries": [],
            "geographies": []
        }

        if len(query) < 2:
            return {
                "suggestions": suggestions,
                "popular_queries": popular_queries,
                "legal_terms": legal_terms,
                "metadata_suggestions": metadata_suggestions
            }

        query_lower = query.lower()

        # Get popular queries from database
        try:
            popular_stmt = (
                select(Query.query_text, func.count(Query.id).label('count'))
                .where(Query.query_text.ilike(f"%{query}%"))
                .group_by(Query.query_text)
                .order_by(func.count(Query.id).desc())
                .limit(5)
            )
            popular_result = await db.execute(popular_stmt)
            popular_queries = [row[0] for row in popular_result.fetchall()]
        except Exception:
            pass

        # Get metadata suggestions
        try:
            # Agreement types
            agreement_stmt = (
                select(DocumentMetadata.agreement_type, func.count(DocumentMetadata.id).label('count'))
                .join(Document)
                .where(
                    and_(
                        Document.processed == True,
                        DocumentMetadata.agreement_type.ilike(f"%{query}%"),
                        DocumentMetadata.agreement_type.isnot(None)
                    )
                )
                .group_by(DocumentMetadata.agreement_type)
                .order_by(func.count(DocumentMetadata.id).desc())
                .limit(5)
            )
            agreement_result = await db.execute(agreement_stmt)
            metadata_suggestions["agreement_types"] = [row[0] for row in agreement_result.fetchall()]

            # Jurisdictions
            jurisdiction_stmt = (
                select(DocumentMetadata.jurisdiction, func.count(DocumentMetadata.id).label('count'))
                .join(Document)
                .where(
                    and_(
                        Document.processed == True,
                        DocumentMetadata.jurisdiction.ilike(f"%{query}%"),
                        DocumentMetadata.jurisdiction.isnot(None)
                    )
                )
                .group_by(DocumentMetadata.jurisdiction)
                .order_by(func.count(DocumentMetadata.id).desc())
                .limit(5)
            )
            jurisdiction_result = await db.execute(jurisdiction_stmt)
            metadata_suggestions["jurisdictions"] = [row[0] for row in jurisdiction_result.fetchall()]

            # Industries
            industry_stmt = (
                select(DocumentMetadata.industry, func.count(DocumentMetadata.id).label('count'))
                .join(Document)
                .where(
                    and_(
                        Document.processed == True,
                        DocumentMetadata.industry.ilike(f"%{query}%"),
                        DocumentMetadata.industry.isnot(None)
                    )
                )
                .group_by(DocumentMetadata.industry)
                .order_by(func.count(DocumentMetadata.id).desc())
                .limit(5)
            )
            industry_result = await db.execute(industry_stmt)
            metadata_suggestions["industries"] = [row[0] for row in industry_result.fetchall()]

            # Geographies
            geography_stmt = (
                select(DocumentMetadata.geography, func.count(DocumentMetadata.id).label('count'))
                .join(Document)
                .where(
                    and_(
                        Document.processed == True,
                        DocumentMetadata.geography.ilike(f"%{query}%"),
                        DocumentMetadata.geography.isnot(None)
                    )
                )
                .group_by(DocumentMetadata.geography)
                .order_by(func.count(DocumentMetadata.id).desc())
                .limit(5)
            )
            geography_result = await db.execute(geography_stmt)
            metadata_suggestions["geographies"] = [row[0] for row in geography_result.fetchall()]

        except Exception:
            pass

        # Generate general suggestions based on query patterns
        if "which" in query_lower or "what" in query_lower:
            suggestions.extend([
                f"Which agreements are governed by {query} law?",
                f"What {query} contracts do we have?",
                f"Show me all {query} agreements"
            ])
        elif "show" in query_lower or "list" in query_lower:
            suggestions.extend([
                f"Show me all {query} documents",
                f"List {query} contracts",
                f"Find {query} agreements"
            ])
        else:
            suggestions.extend([
                f"Which agreements are governed by {query} law?",
                f"Show me all {query} contracts",
                f"Find {query} agreements",
                f"What {query} documents do we have?"
            ])

        # Add legal terms
        legal_terms = [
            "governing law", "jurisdiction", "agreement type", "contract value",
            "effective date", "expiration date", "parties", "industry"
        ]

        return {
            "suggestions": suggestions[:limit],
            "popular_queries": popular_queries,
            "legal_terms": legal_terms,
            "metadata_suggestions": metadata_suggestions
        }
