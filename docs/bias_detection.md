# Bias Detection Service

The Heart of News bias detection service analyzes news articles for various forms of bias and propaganda techniques. This documentation explains how to use the service and interpret its results.

## Overview

The bias detector performs multiple types of analysis on text content:

1. **Political Bias Analysis**: Detects left or right political leaning
2. **Emotional Language Analysis**: Measures emotional vs factual language
3. **Propaganda Technique Detection**: Identifies specific propaganda techniques
4. **Fact-Opinion Ratio**: Calculates the balance between factual statements and opinions

The service combines these metrics to produce an overall bias score.

## Usage

### Basic Usage

```python
from app.services.ai.bias_detector import BiasDetector

# Initialize the detector
detector = BiasDetector()

# Analyze a single article
async def analyze_article(text):
    analysis = await detector.get_full_bias_analysis(text)
    return analysis
```

### Output Format

The `get_full_bias_analysis()` method returns a dictionary with the following structure:

```python
{
    "political_bias": float,         # Range: -1.0 (left) to 1.0 (right)
    "emotional_language": float,     # Range: 0.0 (factual) to 1.0 (emotional)
    "propaganda_techniques": [       # List of detected techniques
        {
            "technique": str,        # Technique name (e.g., "loaded_language")
            "span": (int, int),      # Start and end positions in text
            "text": str,             # The matched text
            "confidence": float,     # Confidence score (0.0-1.0)
            "explanation": str       # Explanation of the technique
        },
        # ...more techniques...
    ],
    "fact_opinion_ratio": float,     # Range: 0.0 (all opinions) to 1.0 (all facts)
    "overall_bias_score": float      # Range: 0.0 (unbiased) to 1.0 (highly biased)
}
```

## Interpretation

### Political Bias
- **-1.0 to -0.5**: Strongly left-leaning
- **-0.5 to -0.2**: Moderately left-leaning
- **-0.2 to 0.2**: Politically balanced/neutral
- **0.2 to 0.5**: Moderately right-leaning
- **0.5 to 1.0**: Strongly right-leaning

### Emotional Language
- **0.0 to 0.3**: Primarily factual, minimal emotional language
- **0.3 to 0.6**: Mixed factual and emotional content
- **0.6 to 1.0**: Highly emotional language

### Propaganda Techniques
The service detects several propaganda techniques:
- **Name Calling**: Using negative labels to discredit without addressing substance
- **Loaded Language**: Using emotional language to influence the audience
- **False Dilemma**: Presenting complex issues as having only two possible options
- **Bandwagon**: Appealing to popularity rather than merit
- **Flag Waving**: Appealing to patriotism to justify actions or positions
- **Doubt Casting**: Suggesting information is unreliable without evidence

### Fact-Opinion Ratio
- **0.0 to 0.3**: Mostly opinions with few factual statements
- **0.3 to 0.7**: Mix of facts and opinions
- **0.7 to 1.0**: Mostly factual statements with few opinions

### Overall Bias Score
- **0.0 to 0.3**: Low bias, generally balanced presentation
- **0.3 to 0.7**: Moderate bias, shows notable partisan or emotional slant
- **0.7 to 1.0**: High bias, strongly partisan or propaganda-like content

## Examples

### Example 1: Neutral Article
```python
analysis = await detector.get_full_bias_analysis(neutral_text)
# Result:
# - political_bias: -0.02 (neutral)
# - emotional_language: 0.12 (factual)
# - propaganda_techniques: [] (none detected)
# - fact_opinion_ratio: 0.85 (mostly factual)
# - overall_bias_score: 0.11 (low bias)
```

### Example 2: Biased Article
```python
analysis = await detector.get_full_bias_analysis(biased_text)
# Result:
# - political_bias: -0.68 (strongly left-leaning)
# - emotional_language: 0.54 (moderately emotional)
# - propaganda_techniques: [5 techniques detected]
# - fact_opinion_ratio: 0.31 (opinion-heavy)
# - overall_bias_score: 0.73 (high bias)
```

## Limitations

- The current implementation uses keyword and pattern matching, which may miss subtle forms of bias
- Cultural and contextual biases may not be detected accurately
- Specialized jargon or domain-specific content may lead to false positives
- The system does not distinguish between different types of sources (news, opinion, etc.)

## Future Improvements

- Integration with transformer-based models for more accurate classification
- Entity recognition to identify and normalize references to people and organizations
- Source reliability metrics integration
- Context-aware bias detection for different domains
- User feedback loop for continuous improvement