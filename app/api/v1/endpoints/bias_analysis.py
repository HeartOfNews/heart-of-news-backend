"""
API endpoints for bias analysis testing
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.bias_detector import BiasDetector

router = APIRouter()


class BiasAnalysisRequest(BaseModel):
    text: str
    detailed: bool = False


class BiasAnalysisResponse(BaseModel):
    political_bias: float
    emotional_language: float
    fact_opinion_ratio: float
    overall_bias_score: float
    risk_assessment: Dict[str, Any]
    recommendations: list[str]
    propaganda_techniques: list[Dict[str, Any]] = None
    detailed_analysis: Dict[str, Any] = None


@router.post("/analyze", response_model=BiasAnalysisResponse)
async def analyze_bias(request: BiasAnalysisRequest) -> Any:
    """
    Analyze bias in provided text
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
    
    if len(request.text) > 50000:
        raise HTTPException(status_code=400, detail="Text too long. Maximum 50,000 characters.")
    
    try:
        bias_detector = BiasDetector()
        analysis = await bias_detector.get_full_bias_analysis(request.text)
        
        response = BiasAnalysisResponse(
            political_bias=analysis["political_bias"],
            emotional_language=analysis["emotional_language"],
            fact_opinion_ratio=analysis["fact_opinion_ratio"],
            overall_bias_score=analysis["overall_bias_score"],
            risk_assessment=analysis["risk_assessment"],
            recommendations=analysis["recommendations"]
        )
        
        if request.detailed:
            response.propaganda_techniques = analysis["propaganda_techniques"]
            response.detailed_analysis = {
                "sentiment_scores": analysis["sentiment_scores"],
                "propaganda_density": analysis["propaganda_density"],
                "bias_indicators": analysis["bias_indicators"],
                "fact_analysis": analysis["fact_analysis"]
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/techniques")
async def get_propaganda_techniques() -> Any:
    """
    Get list of propaganda techniques that can be detected
    """
    from app.services.ai.propaganda_detector import PropagandaTechniqueDetector
    
    detector = PropagandaTechniqueDetector()
    techniques = await detector.get_technique_explanations()
    
    return {"techniques": techniques}


@router.post("/quick-check")
async def quick_bias_check(request: BiasAnalysisRequest) -> Any:
    """
    Quick bias check with just basic metrics
    """
    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
    
    try:
        bias_detector = BiasDetector()
        
        # Run just the basic analyses for speed
        political_bias = await bias_detector.analyze_political_bias(request.text)
        emotional_language = await bias_detector.analyze_emotional_language(request.text)
        fact_opinion_ratio = await bias_detector.calculate_fact_opinion_ratio(request.text)
        
        overall_bias_score = bias_detector._calculate_overall_bias(
            political_bias, emotional_language, 0, fact_opinion_ratio
        )
        
        # Simple risk assessment
        if overall_bias_score > 0.6:
            risk_level = "high"
        elif overall_bias_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "political_bias": political_bias,
            "emotional_language": emotional_language,
            "fact_opinion_ratio": fact_opinion_ratio,
            "overall_bias_score": overall_bias_score,
            "risk_level": risk_level
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")


@router.post("/test-sample")
async def test_with_sample() -> Any:
    """
    Test bias detection with sample texts
    """
    sample_texts = {
        "neutral": "The Federal Reserve announced a 0.25% interest rate increase yesterday. The decision was made after reviewing economic data showing inflation at 3.2% annually. The change affects approximately 150 million borrowers nationwide.",
        
        "biased": "The corrupt establishment once again betrays hardworking Americans with their devastating rate hike! This outrageous decision will destroy families and small businesses while enriching the greedy elite. Every patriotic citizen must stand up against this socialist attack on our freedoms!",
        
        "opinion": "I believe this rate increase is a mistake that will hurt the economy. While inflation is certainly a concern, raising rates now seems premature and could trigger unnecessary hardship for families who are already struggling."
    }
    
    results = {}
    bias_detector = BiasDetector()
    
    for label, text in sample_texts.items():
        analysis = await bias_detector.get_full_bias_analysis(text)
        results[label] = {
            "text": text,
            "political_bias": analysis["political_bias"],
            "emotional_language": analysis["emotional_language"],
            "fact_opinion_ratio": analysis["fact_opinion_ratio"],
            "overall_bias_score": analysis["overall_bias_score"],
            "propaganda_count": len(analysis["propaganda_techniques"]),
            "risk_level": analysis["risk_assessment"]["level"]
        }
    
    return {"sample_analysis": results}