#!/usr/bin/env python3

"""
Script to test the bias detector with sample articles
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ai.bias_detector import BiasDetector


# Sample articles with different bias characteristics
SAMPLE_ARTICLES = {
    "left_biased": """
    BREAKING: Corporate Tax Loopholes Cost Working Families Billions
    
    In a shocking new report, researchers have revealed that major corporations 
    are exploiting tax loopholes that allow them to avoid paying their fair share,
    burdening working families with the costs. Progressive lawmakers are demanding
    immediate regulation of these corporate giants.
    
    "This is a disaster for working Americans," said Senator Smith. "While the wealthy
    elite enjoy record profits, the rest of us are left to pick up the tab."
    
    The report reveals that workers' wages have stagnated while CEO compensation
    has increased by 300%. Experts suggest that increased union membership and 
    social welfare programs could help address this crisis of inequality.
    
    Climate activists have also pointed out that these same corporations are
    major polluters contributing to environmental devastation in marginalized communities.
    """,
    
    "right_biased": """
    ALERT: Government Overreach Threatens American Businesses
    
    A newly proposed set of regulations threatens to strangle American businesses
    with red tape and excessive taxation, according to industry leaders. Conservative
    economic experts warn that these policies will damage our free market economy.
    
    "This is an attack on the constitutional rights of business owners," said industry
    spokesperson Johnson. "The government wants to control every aspect of private enterprise."
    
    The proposal comes as entrepreneurs are already struggling with inflation caused by
    excessive government spending. Patriotic business owners are standing up for traditional
    economic values and fighting for tax cuts that would stimulate growth.
    
    Military and law enforcement groups have expressed concern that weakening American
    businesses could threaten national security and sovereignty.
    """,
    
    "neutral": """
    City Infrastructure Project Begins Next Month
    
    The city council approved the downtown infrastructure renewal project yesterday
    by a vote of 7-2. Construction is scheduled to begin on May 15 and continue
    through October, according to the official timeline released by the public works department.
    
    "We've completed the planning phase and secured the necessary permits," said
    project manager Garcia. "Our team is ready to proceed on schedule."
    
    The $4.2 million project includes road resurfacing, replacement of water mains,
    and installation of energy-efficient street lighting. Traffic will be redirected
    during construction hours of 7am to 5pm on weekdays.
    
    Residents can find more information, including detailed maps of construction zones
    and traffic alternatives, on the city's official website or by calling the project
    information line.
    """
}


async def analyze_articles():
    """Analyze sample articles and print detailed results"""
    
    detector = BiasDetector()
    results = {}
    
    print("\n======================= BIAS DETECTOR TEST =======================\n")
    
    # Analyze each article
    for article_type, text in SAMPLE_ARTICLES.items():
        print(f"Analyzing {article_type} article...")
        analysis = await detector.get_full_bias_analysis(text)
        results[article_type] = analysis
        
        # Print summary
        print(f"\n  Political bias: {analysis['political_bias']:.2f} (-1.0=left, +1.0=right)")
        print(f"  Emotional language: {analysis['emotional_language']:.2f} (0.0=factual, 1.0=emotional)")
        print(f"  Fact-opinion ratio: {analysis['fact_opinion_ratio']:.2f} (0.0=opinion, 1.0=factual)")
        print(f"  Propaganda techniques: {len(analysis['propaganda_techniques'])}")
        print(f"  Overall bias score: {analysis['overall_bias_score']:.2f} (0.0=unbiased, 1.0=biased)")
        
        # Print detected propaganda techniques if any
        if analysis['propaganda_techniques']:
            print("\n  Detected propaganda techniques:")
            for i, technique in enumerate(analysis['propaganda_techniques'][:5], 1):
                print(f"    {i}. {technique['technique']} ({technique['confidence']:.2f})")
                print(f"       \"{technique['text']}\"")
                print(f"       Explanation: {technique['explanation']}")
        
        print("\n" + "-" * 65 + "\n")
    
    # Compare results
    print("COMPARISON SUMMARY:")
    print(f"  Most politically biased: {max(results.items(), key=lambda x: abs(x[1]['political_bias']))[0]}")
    print(f"  Most emotional language: {max(results.items(), key=lambda x: x[1]['emotional_language'])[0]}")
    print(f"  Most factual content: {max(results.items(), key=lambda x: x[1]['fact_opinion_ratio'])[0]}")
    print(f"  Most propaganda techniques: {max(results.items(), key=lambda x: len(x[1]['propaganda_techniques']))[0]}")
    print(f"  Highest overall bias: {max(results.items(), key=lambda x: x[1]['overall_bias_score'])[0]}")
    
    print("\n================================================================\n")


if __name__ == "__main__":
    asyncio.run(analyze_articles())