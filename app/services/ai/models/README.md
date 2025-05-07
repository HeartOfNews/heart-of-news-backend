# Bias Detection Models

This directory contains model files used by the bias detector service.

## Model Types

1. **Political Bias Model**: Detects political bias (left/right leaning)
2. **Emotional Language Model**: Measures emotional vs factual content
3. **Propaganda Detection Model**: Identifies propaganda techniques
4. **Fact vs Opinion Model**: Distinguishes factual statements from opinions

## File Structure

- `political_keywords.json`: Contains left/right leaning political terminology
- `propaganda_patterns.json`: Regex patterns for detecting propaganda techniques
- `emotional_words/`: 
  - `positive_words.txt`: Words with positive emotional connotations
  - `negative_words.txt`: Words with negative emotional connotations
- `transformer_models/`: Directory for pretrained transformer models (if used)

## Installation

1. Download pre-trained models from the project storage:
   ```
   ./scripts/download_models.sh
   ```

2. Verify model installation:
   ```
   python -m app.services.ai.verify_models
   ```

## Custom Training

To train custom models on domain-specific data:

1. Place training data in `training_data/`
2. Run training script:
   ```
   python -m app.services.ai.train_models
   ```
3. Trained models will be saved to this directory

## Model Versions

The current production models:

- Political bias model: v1.2
- Emotional language model: v1.1
- Propaganda detection: v1.3
- Fact-opinion classifier: v1.0