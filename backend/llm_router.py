# File: backend/llm_router.py
from enum import Enum
from typing import Dict, Any, Optional

class ModelType(Enum):
    SMART = "smart"      # High intelligence (e.g., Llama 3 70B, Claude 3.5 Sonnet)
    BALANCED = "balanced" # Mid-tier (e.g., Llama 3 8B, GPT-4o-mini)
    FAST = "fast"         # Speed-optimized (e.g., Phi-3, Gemini Flash)
    CODE = "code"         # Coding specialized (e.g., CodeLlama)

class LLMRouter:
    def __init__(self):
        # Default mapping for phases - these are logic categories
        self.routing_map = {
            "01_ANALYSIS": ModelType.SMART,
            "02_BLUEPRINT": ModelType.SMART,
            "03_AGENT_SPAWN": ModelType.BALANCED,
            "04_BUILD": ModelType.CODE,
            "05_VALIDATION": ModelType.FAST,
            "06_REFINEMENT": ModelType.SMART,
        }

    def get_model_type_for_phase(self, phase: str, complexity: int = 5) -> ModelType:
        """
        Determines the best ModelType based on development phase and task complexity.
        """
        model_type = self.routing_map.get(phase, ModelType.BALANCED)
        
        # Override for high-complexity tasks
        if complexity > 8:
            model_type = ModelType.SMART
            
        return model_type

    def resolve_actual_model(self, model_type: ModelType, engine_name: str, config_models: Optional[list] = None) -> str:
        """
        Resolves a generic ModelType to a specific model name supported by the given engine.
        """
        engine = engine_name.lower()
        
        # Simple mapping for Ollama as a primary example
        if "ollama" in engine:
            mapping = {
                ModelType.SMART: "llama3:70b",
                ModelType.BALANCED: "llama3",
                ModelType.FAST: "phi3",
                ModelType.CODE: "codellama"
            }
        elif "perplexity" in engine:
            mapping = {
                ModelType.SMART: "llama-3-sonar-large-32k-online",
                ModelType.BALANCED: "llama-3-sonar-small-32k-chat",
                ModelType.FAST: "llama-3-sonar-small-32k-chat",
                ModelType.CODE: "llama-3-sonar-large-32k-chat"
            }
        else:
            # Fallback to whatever is active in config if we don't have a specialized map
            return "default"

        return mapping.get(model_type, "default")

llm_router = LLMRouter()
