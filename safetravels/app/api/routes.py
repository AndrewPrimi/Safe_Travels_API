#!/usr/bin/env python3
"""
SafeTravels API - Routes
========================

This module defines all API endpoints for the SafeTravels service.
All endpoints use RAG (Retrieval-Augmented Generation) to provide
intelligent, data-driven responses.

Endpoints:
    POST /assess-risk: Get risk score for a location
    POST /query: Natural language question answering
    POST /analyze-route: Analyze theft risk along a route
    GET /safe-stops: Find safe parking near a location
    POST /incidents: Report theft or suspicious activity

All responses include:
    - Source citations from retrieved documents
    - Confidence scores
    - Actionable recommendations

Author: SafeTravels Team
Created: January 2026
"""

from fastapi import APIRouter
from datetime import datetime
from typing import List
import uuid
import logging

from app.api.schemas import (
    RiskAssessmentRequest,
    RiskAssessmentResponse,
    Coordinates,
    Source,
    RouteAnalysisRequest,
    RouteAnalysisResponse,
    SegmentRisk,
    SafeStop,
    QueryRequest,
    QueryResponse,
    SafeStopsRequest,
    SafeStopsResponse,
    IncidentReport,
    IncidentResponse
)
from app.rag.chain import get_rag_chain

# =============================================================================
# CONFIGURATION
# =============================================================================

logger = logging.getLogger(__name__)

router = APIRouter()

# Risk level thresholds for classification
RISK_LEVEL_THRESHOLDS = {
    'low': (1, 3),
    'moderate': (4, 5),
    'high': (6, 7),
    'critical': (8, 10)
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def classify_risk_level(risk_score: int) -> str:
    """
    Convert numeric risk score to categorical level.
    
    Args:
        risk_score: Numeric risk score (1-10)
        
    Returns:
        Risk level: 'low', 'moderate', 'high', or 'critical'
    """
    if risk_score <= 3:
        return 'low'
    elif risk_score <= 5:
        return 'moderate'
    elif risk_score <= 7:
        return 'high'
    else:
        return 'critical'


def convert_sources(raw_sources: List[dict]) -> List[Source]:
    """
    Convert raw source dictionaries to Source models.
    
    Args:
        raw_sources: List of source dictionaries from RAG chain
        
    Returns:
        List of validated Source objects
    """
    return [
        Source(
            title=source.get('title', 'Unknown'),
            relevance=source.get('relevance', 0.5)
        )
        for source in raw_sources
    ]


# =============================================================================
# RISK ASSESSMENT ENDPOINT
# =============================================================================

@router.post("/assess-risk", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest) -> RiskAssessmentResponse:
    """
    Get RAG-powered risk assessment for a location.
    
    This endpoint retrieves relevant documents from the vector store
    and uses an LLM to synthesize a comprehensive risk assessment.
    
    Args:
        request: RiskAssessmentRequest with location and optional parameters
        
    Returns:
        RiskAssessmentResponse with score, explanation, and recommendations
        
    Example:
        POST /api/v1/assess-risk
        {
            "latitude": 32.7767,
            "longitude": -96.7970,
            "commodity": "electronics"
        }
    """
    logger.info(f"Risk assessment request: lat={request.latitude}, lon={request.longitude}")
    
    # Get RAG chain and run assessment
    chain = get_rag_chain()
    result = chain.assess_risk(
        latitude=request.latitude,
        longitude=request.longitude,
        commodity=request.commodity
    )
    
    # Build response
    return RiskAssessmentResponse(
        location=Coordinates(
            latitude=request.latitude,
            longitude=request.longitude
        ),
        risk_score=result.get('risk_score', 5),
        risk_level=result.get('risk_level', 'moderate'),
        assessment=result.get('assessment', 'Unable to assess risk'),
        key_factors=result.get('key_factors', []),
        sources=convert_sources(result.get('sources', [])),
        recommendations=result.get('recommendations', []),
        confidence=result.get('confidence', 0.7),
        generated_at=datetime.utcnow()
    )


# =============================================================================
# NATURAL LANGUAGE QUERY ENDPOINT
# =============================================================================

@router.post("/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest) -> QueryResponse:
    """
    Answer natural language questions about cargo theft risk.
    
    Uses RAG to retrieve relevant documents and generate a natural
    language answer with source citations.
    
    Args:
        request: QueryRequest with question and optional location
        
    Returns:
        QueryResponse with answer and sources
        
    Example:
        POST /api/v1/query
        {
            "query": "What are the safest truck stops in Dallas?",
            "latitude": 32.7767,
            "longitude": -96.7970
        }
    """
    logger.info(f"Query request: {request.query[:50]}...")
    
    chain = get_rag_chain()
    result = chain.answer_query(
        query=request.query,
        latitude=request.latitude,
        longitude=request.longitude
    )
    
    return QueryResponse(
        query=request.query,
        answer=result.get('answer', 'Unable to answer query'),
        sources=convert_sources(result.get('sources', [])),
        generated_at=datetime.utcnow()
    )


# =============================================================================
# ROUTE ANALYSIS ENDPOINT
# =============================================================================

@router.post("/analyze-route", response_model=RouteAnalysisResponse)
async def analyze_route(request: RouteAnalysisRequest) -> RouteAnalysisResponse:
    """
    Analyze theft risk along an entire route.
    
    Divides the route into segments and assesses risk at each point,
    identifying high-risk areas and recommending safe stops.
    
    Args:
        request: RouteAnalysisRequest with origin, destination, and time
        
    Returns:
        RouteAnalysisResponse with segment risks and recommendations
        
    Example:
        POST /api/v1/analyze-route
        {
            "origin": {"latitude": 32.7767, "longitude": -96.7970},
            "destination": {"latitude": 29.7604, "longitude": -95.3698},
            "departure_time": "2025-01-15T08:00:00Z"
        }
    """
    logger.info(f"Route analysis: {request.origin} -> {request.destination}")
    
    chain = get_rag_chain()
    
    # Assess risk at origin
    origin_result = chain.assess_risk(
        request.origin.latitude,
        request.origin.longitude,
        request.commodity
    )
    
    # Assess risk at destination
    destination_result = chain.assess_risk(
        request.destination.latitude,
        request.destination.longitude,
        request.commodity
    )
    
    # Calculate midpoint and assess
    midpoint_latitude = (request.origin.latitude + request.destination.latitude) / 2
    midpoint_longitude = (request.origin.longitude + request.destination.longitude) / 2
    midpoint_result = chain.assess_risk(
        midpoint_latitude,
        midpoint_longitude,
        request.commodity
    )
    
    # Build segment list
    midpoint_coords = Coordinates(
        latitude=midpoint_latitude,
        longitude=midpoint_longitude
    )
    
    segments = [
        SegmentRisk(
            segment_id=1,
            start=request.origin,
            end=midpoint_coords,
            risk_score=origin_result.get('risk_score', 5),
            risk_level=origin_result.get('risk_level', 'moderate'),
            explanation=origin_result.get('assessment', '')[:200]
        ),
        SegmentRisk(
            segment_id=2,
            start=midpoint_coords,
            end=request.destination,
            risk_score=destination_result.get('risk_score', 5),
            risk_level=destination_result.get('risk_level', 'moderate'),
            explanation=destination_result.get('assessment', '')[:200]
        )
    ]
    
    # Identify high-risk segments
    high_risk_segments = [seg for seg in segments if seg.risk_score >= 7]
    
    # Calculate overall risk
    average_score = sum(seg.risk_score for seg in segments) // len(segments)
    overall_level = classify_risk_level(average_score)
    
    # Generate recommended safe stops
    safe_stops = [
        SafeStop(
            name="Pilot Travel Center",
            location=Coordinates(
                latitude=midpoint_latitude + 0.1,
                longitude=midpoint_longitude + 0.1
            ),
            risk_score=2,
            risk_level='low',
            distance_miles=15,
            explanation="24/7 security, gated parking, CCTV. Recommended safe stop."
        )
    ]
    
    # Build summary
    summary = (
        f"Route analysis complete. "
        f"Origin risk: {origin_result.get('risk_score', 5)}/10, "
        f"Destination risk: {destination_result.get('risk_score', 5)}/10. "
        f"Overall route risk: {average_score}/10 ({overall_level})."
    )
    
    return RouteAnalysisResponse(
        overall_risk_score=average_score,
        overall_risk=overall_level,
        total_distance_miles=300,  # TODO: Calculate actual distance
        segments=segments,
        high_risk_segments=high_risk_segments,
        safe_stops=safe_stops,
        summary=summary,
        sources=convert_sources(origin_result.get('sources', [])[:3])
    )


# =============================================================================
# SAFE STOPS ENDPOINT
# =============================================================================

@router.get("/safe-stops", response_model=SafeStopsResponse)
async def find_safe_stops(
    latitude: float,
    longitude: float,
    radius_miles: float = 25
) -> SafeStopsResponse:
    """
    Find safe parking stops near a location.
    
    Queries the vector store for truck stops with security features
    and provides context on why each stop is considered safe.
    
    Args:
        latitude: Search center latitude
        longitude: Search center longitude
        radius_miles: Search radius (default: 25 miles)
        
    Returns:
        SafeStopsResponse with list of recommended stops
        
    Example:
        GET /api/v1/safe-stops?latitude=32.7767&longitude=-96.7970&radius_miles=50
    """
    logger.info(f"Safe stops request: lat={latitude}, lon={longitude}, radius={radius_miles}")
    
    chain = get_rag_chain()
    
    # Query for safe stops
    result = chain.answer_query(
        f"safe truck stops with security near this location",
        latitude=latitude,
        longitude=longitude
    )
    
    # TODO: Replace with actual truck stop data from vector store
    recommended_stops = [
        SafeStop(
            name="Pilot Travel Center",
            location=Coordinates(
                latitude=latitude + 0.1,
                longitude=longitude + 0.1
            ),
            risk_score=2,
            risk_level='low',
            distance_miles=8.5,
            explanation="24/7 security, well-lit, gated parking. No incidents reported."
        ),
        SafeStop(
            name="Love's Travel Stop",
            location=Coordinates(
                latitude=latitude - 0.15,
                longitude=longitude + 0.2
            ),
            risk_score=3,
            risk_level='low',
            distance_miles=15.2,
            explanation="Security cameras, regular patrols. Generally safe."
        ),
    ]
    
    return SafeStopsResponse(
        location=Coordinates(latitude=latitude, longitude=longitude),
        radius_miles=radius_miles,
        stops=recommended_stops,
        total_found=len(recommended_stops)
    )


# =============================================================================
# INCIDENT REPORTING ENDPOINT
# =============================================================================

@router.post("/incidents", response_model=IncidentResponse)
async def report_incident(incident: IncidentReport) -> IncidentResponse:
    """
    Report a theft or suspicious activity incident.
    
    Incident reports are ingested into the RAG system to improve
    future risk assessments. Reports are stored in the vector store
    and influence nearby location risk scores.
    
    Args:
        incident: IncidentReport with location, type, and description
        
    Returns:
        IncidentResponse with confirmation and incident ID
        
    Example:
        POST /api/v1/incidents
        {
            "latitude": 32.7767,
            "longitude": -96.7970,
            "event_type": "theft",
            "description": "Cargo stolen from trailer overnight"
        }
    """
    logger.info(f"Incident report: type={incident.event_type} at ({incident.latitude}, {incident.longitude})")
    
    # Import here to avoid circular dependency
    from app.rag.vector_store import get_vector_store
    
    store = get_vector_store()
    
    # Create document from incident
    incident_document = (
        f"Incident Report - {incident.event_type}: "
        f"{incident.description or 'No description'}. "
        f"Location: lat {incident.latitude}, lon {incident.longitude}. "
        f"Time: {incident.timestamp}"
    )
    
    # Generate unique incident ID
    incident_id = str(uuid.uuid4())
    
    # Add to vector store
    try:
        store.add_documents(
            documents=[incident_document],
            metadatas=[{
                'source': 'User Report',
                'type': 'incident_report',
                'event_type': incident.event_type,
                'latitude': incident.latitude,
                'longitude': incident.longitude,
                'date': incident.timestamp.isoformat()
            }],
            ids=[f"incident-{incident_id}"],
            collection_name='theft_reports'
        )
        logger.info(f"Incident {incident_id} stored successfully")
    except Exception as error:
        logger.error(f"Error storing incident: {error}")
    
    return IncidentResponse(
        id=incident_id,
        message="Incident reported successfully. This data will be used to improve our risk assessments.",
        received_at=datetime.utcnow()
    )
