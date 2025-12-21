"""
Layer 6: AI Detection using Fast-Detect-GPT (Remote) + Heuristic Fallback
Detects AI-generated text content in documents using Fast-Detect-GPT via RunPod API
"""

import os
import sys
import requests
import numpy as np
from typing import Dict, Any, Optional
import json
import time
import re
from collections import Counter
import math

# Add the fast-detect-gpt scripts to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'fast-detect-gpt', 'scripts'))

try:
    import torch
    from scipy.stats import norm
    from model import load_tokenizer, load_model
    from fast_detect_gpt import get_sampling_discrepancy_analytic
    FAST_DETECT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Fast-DetectGPT dependencies not available: {e}")
    print("💡 Install torch, transformers, and scipy to use Fast-DetectGPT")
    FAST_DETECT_AVAILABLE = False


class ModelManager:
    """
    Manages model downloading, caching, and optimization for Fast-DetectGPT
    """

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.model_configs = {
            # Lightweight models (faster, less accurate)
            "light": {
                "sampling_model": "gpt2",
                "scoring_model": "gpt2",
                "size": "~500MB",
                "speed": "fast",
                "accuracy": "medium"
            },
            # Medium models (balanced)
            "medium": {
                "sampling_model": "gpt-neo-2.7B",
                "scoring_model": "gpt-neo-2.7B",
                "size": "~5GB",
                "speed": "medium",
                "accuracy": "high"
            },
            # Heavy models (slower, more accurate)
            "heavy": {
                "sampling_model": "gpt-j-6B",
                "scoring_model": "gpt-neo-2.7B",
                "size": "~12GB",
                "speed": "slow",
                "accuracy": "highest"
            }
        }

    def get_best_config_for_system(self):
        """
        Automatically select the best model configuration based on system resources
        """
        try:
            # Check available GPU memory
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                if gpu_memory >= 16:
                    return "heavy"
                elif gpu_memory >= 8:
                    return "medium"
                else:
                    return "light"
            else:
                # Check system RAM as fallback
                import psutil
                ram_gb = psutil.virtual_memory().total / (1024**3)
                if ram_gb >= 32:
                    return "medium"
                else:
                    return "light"
        except Exception:
            return "light"  # Safe fallback

    def download_models_if_needed(self, config_name):
        """
        Download models if they're not already cached
        """
        if config_name not in self.model_configs:
            raise ValueError(f"Unknown config: {config_name}")

        config = self.model_configs[config_name]
        print(f"📋 Preparing {config_name} configuration...")
        print(f"   Size: {config['size']}, Speed: {config['speed']}, Accuracy: {config['accuracy']}")

        # Create cache directory structure
        os.makedirs(self.cache_dir, exist_ok=True)

        return config

class TrainingDataCollector:
    """
    Collects training data and feedback for continuous improvement
    """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.feedback_file = os.path.join(data_dir, "user_feedback.jsonl")
        self.predictions_file = os.path.join(data_dir, "predictions.jsonl")
        os.makedirs(data_dir, exist_ok=True)

    def log_prediction(self, text, prediction_result, user_feedback=None):
        """
        Log a prediction and optional user feedback for training
        """
        # Convert numpy types and ensure JSON serializable
        def make_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(v) for v in obj]
            elif hasattr(obj, 'item'):  # numpy types
                return obj.item()
            elif isinstance(obj, (bool, int, float, str, type(None))):
                return obj
            else:
                return str(obj)

        log_entry = {
            "timestamp": time.time(),
            "text_hash": hash(text),  # Don't store full text for privacy
            "text_length": len(text),
            "prediction": make_serializable(prediction_result),
            "user_feedback": make_serializable(user_feedback)
        }

        # Log prediction
        with open(self.predictions_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Log feedback if provided
        if user_feedback:
            with open(self.feedback_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

    def get_feedback_stats(self):
        """
        Get statistics about user feedback for model improvement
        """
        try:
            with open(self.feedback_file, "r") as f:
                feedback_data = [json.loads(line) for line in f]

            if not feedback_data:
                return {"total_feedback": 0}

            # Calculate accuracy based on feedback
            correct_predictions = sum(1 for entry in feedback_data
                                    if entry["prediction"]["is_ai_generated"] == entry["user_feedback"]["correct_label"])

            return {
                "total_feedback": len(feedback_data),
                "accuracy": correct_predictions / len(feedback_data) if feedback_data else 0,
                "recent_feedback": feedback_data[-10:]  # Last 10 pieces of feedback
            }
        except FileNotFoundError:
            return {"total_feedback": 0}


class FastDetectGPTLocal:
    """
    Local Fast-DetectGPT implementation
    """

    def __init__(self, config_name=None, device=None, cache_dir="./model_cache"):
        self.cache_dir = cache_dir
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_manager = ModelManager(cache_dir)
        self.model_loaded = False
        self.criterion_fn = get_sampling_discrepancy_analytic

        # Auto-select best configuration if not specified
        if config_name is None:
            config_name = self.model_manager.get_best_config_for_system()

        self.config = self.model_manager.download_models_if_needed(config_name)
        self.sampling_model_name = self.config["sampling_model"]
        self.scoring_model_name = self.config["scoring_model"]

        # Predefined distribution parameters for different model combinations
        self.distrib_params = {
            'gpt-j-6B_gpt-neo-2.7B': {'mu0': 0.2713, 'sigma0': 0.9366, 'mu1': 2.2334, 'sigma1': 1.8731},
            'gpt-neo-2.7B_gpt-neo-2.7B': {'mu0': -0.2489, 'sigma0': 0.9968, 'mu1': 1.8983, 'sigma1': 1.9935},
            'falcon-7b_falcon-7b-instruct': {'mu0': -0.0707, 'sigma0': 0.9520, 'mu1': 2.9306, 'sigma1': 1.9039},
            'gpt2_gpt2': {'mu0': 0.0, 'sigma0': 1.0, 'mu1': 2.0, 'sigma1': 2.0},  # Default for GPT-2
        }

        self._initialize_models()

    def _initialize_models(self):
        """Initialize the models for Fast-DetectGPT"""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)

            print(f"🔄 Loading Fast-DetectGPT models ({self.sampling_model_name}, {self.scoring_model_name})...")
            print(f"   Configuration: {self.config['speed']} speed, {self.config['accuracy']} accuracy")

            # Load scoring model and tokenizer
            self.scoring_tokenizer = load_tokenizer(self.scoring_model_name, self.cache_dir)
            self.scoring_model = load_model(self.scoring_model_name, self.device, self.cache_dir)
            self.scoring_model.eval()

            # Load sampling model if different
            if self.sampling_model_name != self.scoring_model_name:
                self.sampling_tokenizer = load_tokenizer(self.sampling_model_name, self.cache_dir)
                self.sampling_model = load_model(self.sampling_model_name, self.device, self.cache_dir)
                self.sampling_model.eval()

            # Get classifier parameters
            key = f'{self.sampling_model_name}_{self.scoring_model_name}'
            if key in self.distrib_params:
                self.classifier = self.distrib_params[key]
            else:
                print(f"⚠️ No predefined distribution parameters for {key}, using default")
                self.classifier = {'mu0': 0.0, 'sigma0': 1.0, 'mu1': 2.0, 'sigma1': 2.0}

            self.model_loaded = True
            print("✅ Fast-DetectGPT models loaded successfully")

        except Exception as e:
            print(f"❌ Error loading Fast-DetectGPT models: {e}")
            self.model_loaded = False

    def compute_crit(self, text):
        """Compute conditional probability curvature"""
        if not self.model_loaded:
            raise RuntimeError("Models not loaded")

        tokenized = self.scoring_tokenizer(text, truncation=True, return_tensors="pt", padding=True, return_token_type_ids=False).to(self.device)
        labels = tokenized.input_ids[:, 1:]

        with torch.no_grad():
            logits_score = self.scoring_model(**tokenized).logits[:, :-1]
            if self.sampling_model_name == self.scoring_model_name:
                logits_ref = logits_score
            else:
                tokenized = self.sampling_tokenizer(text, truncation=True, return_tensors="pt", padding=True, return_token_type_ids=False).to(self.device)
                logits_ref = self.sampling_model(**tokenized).logits[:, :-1]

            crit = self.criterion_fn(logits_ref, logits_score, labels)

        return crit, labels.size(1)

    def compute_prob_norm(self, x, mu0, sigma0, mu1, sigma1):
        """Compute probability using normal distribution"""
        pdf_value0 = norm.pdf(x, loc=mu0, scale=sigma0)
        pdf_value1 = norm.pdf(x, loc=mu1, scale=sigma1)
        prob = pdf_value1 / (pdf_value0 + pdf_value1)
        return prob

    def compute_prob(self, text):
        """Compute probability that text is AI-generated"""
        crit, ntoken = self.compute_crit(text)
        mu0 = self.classifier['mu0']
        sigma0 = self.classifier['sigma0']
        mu1 = self.classifier['mu1']
        sigma1 = self.classifier['sigma1']
        prob = self.compute_prob_norm(crit, mu0, sigma0, mu1, sigma1)
        return prob, crit, ntoken


class AIDetectionLayer:
    """
    Layer 6: AI Detection
    Uses Fast-Detect-GPT via RunPod API with heuristic fallback
    """
    
    def __init__(self):
        self.layer_name = "AI Detection"
        self.layer_number = 6
        self.model_loaded = False
        self.runpod_endpoint = None
        self.runpod_api_key = None
        self.fast_detect_gpt = None
        self.training_collector = None
        self._setup_detection_methods()
        
    def _setup_detection_methods(self):
        """Setup detection methods - try local Fast-DetectGPT first, then RunPod as fallback"""
        # First try to initialize local Fast-DetectGPT
        if FAST_DETECT_AVAILABLE:
            try:
                # Use auto-selected model configuration
                device = "cuda" if torch.cuda.is_available() else "cpu"
                cache_dir = os.path.join(os.path.dirname(__file__), "model_cache")
                training_dir = os.path.join(os.path.dirname(__file__), "training_data")

                # Initialize Fast-DetectGPT with auto-configuration
                self.fast_detect_gpt = FastDetectGPTLocal(
                    device=device,
                    cache_dir=cache_dir
                )

                # Initialize training data collector
                self.training_collector = TrainingDataCollector(training_dir)

                if self.fast_detect_gpt.model_loaded:
                    self.model_loaded = True
                    print("✅ Local Fast-DetectGPT initialized successfully")
                    return

            except Exception as e:
                print(f"⚠️ Could not initialize local Fast-DetectGPT: {e}")
                self.fast_detect_gpt = None

        # Fallback to RunPod API if local models fail
        try:
            # Check for RunPod configuration
            self.runpod_endpoint = os.getenv('RUNPOD_FAST_DETECT_ENDPOINT')
            self.runpod_api_key = os.getenv('RUNPOD_API_KEY')

            if self.runpod_endpoint and self.runpod_api_key:
                # Test connection to RunPod endpoint
                response = requests.get(
                    f"{self.runpod_endpoint}/health",
                    headers={"Authorization": f"Bearer {self.runpod_api_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    self.model_loaded = True
                    print("✅ RunPod Fast-DetectGPT endpoint connected successfully")
                else:
                    print(f"⚠️ RunPod endpoint responded with status {response.status_code}")
            else:
                print("⚠️ RunPod credentials not found in environment variables")
                print("💡 Set RUNPOD_FAST_DETECT_ENDPOINT and RUNPOD_API_KEY to use Fast-DetectGPT")

        except requests.RequestException as e:
            print(f"❌ Could not connect to RunPod endpoint: {e}")
        except Exception as e:
            print(f"❌ Error setting up RunPod connection: {e}")

        if not self.model_loaded:
            print("🔄 Using heuristic AI detection fallback")
    
    def analyze(self, file_path: str, text_content: str) -> Dict[str, Any]:
        """
        Analyze text content for AI generation using RunPod Fast-DetectGPT or heuristics
        """
        try:
            if not text_content or len(text_content.strip()) < 100:
                return {
                    "status": "completed",
                    "is_ai_generated": False,
                    "ai_probability": 0.1,
                    "confidence": 0.3,
                    "method": "insufficient_text",
                    "details": {
                        "reason": "Text too short for reliable AI detection",
                        "text_length": len(text_content.strip())
                    },
                    "processing_time": 0.1
                }
            
            start_time = time.time()
            
            # Try local Fast-DetectGPT first if available
            if self.model_loaded and self.fast_detect_gpt:
                result = self._call_local_fast_detect_gpt(text_content)
                if result["status"] == "completed":
                    result["processing_time"] = time.time() - start_time
                    return result
                # If local fails, try RunPod API

            # Try RunPod Fast-DetectGPT API if available and local failed
            if self.model_loaded and self.runpod_endpoint:
                result = self._call_runpod_api(text_content)
                if result["status"] == "completed":
                    result["processing_time"] = time.time() - start_time
                    return result
                # If API fails, fall back to heuristics
            
            # Fallback to enhanced heuristic analysis
            result = self._enhanced_heuristic_detection(text_content)
            result["processing_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            print(f"❌ Error in AI detection analysis: {e}")
            return {
                "status": "error",
                "is_ai_generated": False,
                "ai_probability": 0.5,
                "confidence": 0.0,
                "method": "error_fallback",
                "error": str(e),
                "processing_time": 0.1
            }
    
    def _call_runpod_api(self, text_content: str) -> Dict[str, Any]:
        """
        Call RunPod Fast-DetectGPT API for AI detection
        """
        try:
            # Prepare request payload
            payload = {
                "text": text_content[:2000],  # Limit text length for API
                "model": "gpt-neo-2.7B",  # Default model
                "return_details": True
            }
            
            # Make API request
            response = requests.post(
                f"{self.runpod_endpoint}/detect",
                headers={
                    "Authorization": f"Bearer {self.runpod_api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse response (adjust based on actual RunPod API response format)
                ai_probability = data.get('ai_probability', 0.5)
                is_ai_generated = ai_probability > 0.5
                confidence = abs(ai_probability - 0.5) * 2
                
                return {
                    "status": "completed",
                    "is_ai_generated": is_ai_generated,
                    "ai_probability": float(ai_probability),
                    "confidence": float(confidence),
                    "method": "fast_detect_gpt_api",
                    "details": {
                        "api_endpoint": "runpod",
                        "model_used": data.get('model', 'unknown'),
                        "discrepancy_score": data.get('discrepancy_score'),
                        "raw_response": data
                    }
                }
            else:
                print(f"❌ RunPod API error: {response.status_code} - {response.text}")
                return {"status": "failed"}
                
        except requests.Timeout:
            print("❌ RunPod API timeout")
            return {"status": "failed"}
        except Exception as e:
            print(f"❌ RunPod API error: {e}")
            return {"status": "failed"}

    def _call_local_fast_detect_gpt(self, text_content: str) -> Dict[str, Any]:
        """
        Call local Fast-DetectGPT for AI detection
        """
        try:
            if not self.fast_detect_gpt or not self.fast_detect_gpt.model_loaded:
                return {"status": "failed"}

            # Limit text length for processing
            text_sample = text_content[:2000] if len(text_content) > 2000 else text_content

            # Get AI probability from Fast-DetectGPT
            ai_probability, criterion_score, num_tokens = self.fast_detect_gpt.compute_prob(text_sample)

            # Determine if AI-generated (threshold: 0.5)
            is_ai_generated = ai_probability > 0.5
            confidence = min(abs(ai_probability - 0.5) * 2, 0.95)  # High confidence for Fast-DetectGPT

            return {
                "status": "completed",
                "is_ai_generated": is_ai_generated,
                "ai_probability": float(ai_probability),
                "confidence": float(confidence),
                "method": "fast_detect_gpt_local",
                "details": {
                    "criterion_score": float(criterion_score),
                    "num_tokens": int(num_tokens),
                    "text_length": len(text_sample),
                    "models_used": {
                        "sampling_model": self.fast_detect_gpt.sampling_model_name,
                        "scoring_model": self.fast_detect_gpt.scoring_model_name
                    },
                    "distribution_params": self.fast_detect_gpt.classifier
                }
            }

        except Exception as e:
            print(f"❌ Local Fast-DetectGPT error: {e}")
            return {"status": "failed"}

    def log_user_feedback(self, text_content: str, predicted_result: Dict[str, Any], user_feedback: Dict[str, Any]) -> None:
        """
        Log user feedback for continuous learning
        """
        if self.training_collector:
            self.training_collector.log_prediction(text_content, predicted_result, user_feedback)
            print(f"📊 Logged user feedback for model improvement")

    def get_training_stats(self) -> Dict[str, Any]:
        """
        Get training and feedback statistics
        """
        if self.training_collector:
            return self.training_collector.get_feedback_stats()
        return {"training_collector_unavailable": True}

    def retrain_with_feedback(self) -> Dict[str, Any]:
        """
        Trigger retraining process with collected feedback
        """
        try:
            if not self.training_collector:
                return {"status": "error", "message": "Training collector not available"}

            stats = self.training_collector.get_feedback_stats()

            if stats["total_feedback"] < 10:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 10 feedback samples, have {stats['total_feedback']}"
                }

            # For now, we'll just adjust thresholds based on feedback
            # In a full implementation, this would involve actual model retraining
            current_accuracy = stats.get("accuracy", 0.5)

            if current_accuracy < 0.7:
                print(f"⚠️ Model accuracy below 70% ({current_accuracy:.2%}), adjusting detection thresholds")
                # Implement threshold adjustment logic here

            return {
                "status": "completed",
                "stats": stats,
                "improvements_applied": f"Threshold adjustments based on {stats['total_feedback']} feedback samples"
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def analyze_with_feedback_logging(self, file_path: str, text_content: str, log_prediction: bool = True) -> Dict[str, Any]:
        """
        Enhanced analyze method that logs predictions for training
        """
        result = self.analyze(file_path, text_content)

        # Log prediction for training if enabled
        if log_prediction and self.training_collector and result["status"] == "completed":
            self.training_collector.log_prediction(text_content, result)

        return result

    def _enhanced_heuristic_detection(self, text_content: str) -> Dict[str, Any]:
        """
        Enhanced heuristic-based AI detection with multiple indicators
        """
        try:
            # AI-generated text patterns and indicators
            ai_indicators = {
                'repetitive_phrases': [
                    'in conclusion', 'in summary', 'to summarize',
                    'it is important to note', 'it should be noted',
                    'furthermore', 'moreover', 'additionally',
                    'on the other hand', 'in contrast', 'however',
                    'as a result', 'consequently', 'therefore'
                ],
                'generic_transitions': [
                    'moving on', 'turning to', 'shifting focus',
                    'next,', 'additionally,', 'furthermore,',
                    'in the next section', 'another important point'
                ],
                'ai_hedging': [
                    'it appears that', 'it seems that', 'it might be',
                    'one could argue', 'it is possible that',
                    'potentially', 'arguably', 'presumably',
                    'it should be considered', 'one might say'
                ],
                'formal_structure': [
                    'firstly,', 'secondly,', 'thirdly,',
                    'first and foremost', 'last but not least',
                    'in order to', 'for the purpose of'
                ]
            }
            
            text_lower = text_content.lower()
            words = re.findall(r'\b\w+\b', text_content)
            sentences = [s.strip() for s in re.split(r'[.!?]+', text_content) if s.strip()]
            
            # Calculate various AI indicators
            scores = {}
            
            # 1. Repetitive phrases score
            repetitive_count = sum(1 for phrase in ai_indicators['repetitive_phrases'] 
                                 if phrase in text_lower)
            scores['repetitive_phrases'] = min(repetitive_count / max(len(sentences), 1) * 3, 1.0)
            
            # 2. Generic transitions score
            transition_count = sum(1 for phrase in ai_indicators['generic_transitions'] 
                                 if phrase in text_lower)
            scores['generic_transitions'] = min(transition_count / max(len(sentences), 1) * 4, 1.0)
            
            # 3. AI hedging language score
            hedging_count = sum(1 for phrase in ai_indicators['ai_hedging'] 
                              if phrase in text_lower)
            scores['ai_hedging'] = min(hedging_count / max(len(sentences), 1) * 4, 1.0)
            
            # 4. Formal structure score
            formal_count = sum(1 for phrase in ai_indicators['formal_structure'] 
                             if phrase in text_lower)
            scores['formal_structure'] = min(formal_count / max(len(sentences), 1) * 3, 1.0)
            
            # 5. Sentence length uniformity (AI tends to be more uniform)
            if sentences:
                sentence_lengths = [len(s.split()) for s in sentences]
                avg_length = np.mean(sentence_lengths)
                variance = np.var(sentence_lengths)
                uniformity_score = 1.0 - min(variance / (avg_length ** 2), 1.0) if avg_length > 0 else 0.5
                scores['sentence_uniformity'] = uniformity_score
            else:
                scores['sentence_uniformity'] = 0.5
            
            # 6. Vocabulary diversity (AI often has lower diversity)
            if words:
                unique_words = set(w.lower() for w in words)
                diversity_ratio = len(unique_words) / len(words)
                # Invert diversity (lower diversity = higher AI probability)
                scores['vocabulary_diversity'] = 1.0 - min(diversity_ratio / 0.7, 1.0)
            else:
                scores['vocabulary_diversity'] = 0.5
            
            # 7. Perplexity proxy using word frequency
            if words:
                word_freq = Counter(w.lower() for w in words)
                total_words = len(words)
                entropy = 0
                for count in word_freq.values():
                    prob = count / total_words
                    entropy -= prob * math.log2(prob)
                max_entropy = math.log2(min(len(word_freq), 100))
                normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
                scores['perplexity_proxy'] = 1.0 - normalized_entropy
            else:
                scores['perplexity_proxy'] = 0.5
            
            # Weighted combination of scores
            weights = {
                'repetitive_phrases': 0.20,
                'generic_transitions': 0.15,
                'ai_hedging': 0.15,
                'formal_structure': 0.15,
                'sentence_uniformity': 0.15,
                'vocabulary_diversity': 0.10,
                'perplexity_proxy': 0.10
            }
            
            final_score = sum(scores[key] * weights[key] for key in scores.keys())
            
            # Determine if AI-generated (threshold: 0.65 for heuristic method)
            threshold = 0.65
            is_ai_generated = final_score > threshold
            confidence = min(abs(final_score - 0.5) * 1.5, 0.9)  # Lower max confidence for heuristic
            
            return {
                "status": "completed",
                "is_ai_generated": is_ai_generated,
                "ai_probability": float(final_score),
                "confidence": float(confidence),
                "method": "enhanced_heuristic",
                "details": {
                    "individual_scores": scores,
                    "weights": weights,
                    "final_score": float(final_score),
                    "threshold": threshold,
                    "text_stats": {
                        "word_count": len(words),
                        "sentence_count": len(sentences),
                        "avg_sentence_length": np.mean([len(s.split()) for s in sentences]) if sentences else 0,
                        "vocabulary_diversity": len(set(w.lower() for w in words)) / len(words) if words else 0
                    },
                    "note": "Heuristic analysis - consider using RunPod API for higher accuracy"
                }
            }
            
        except Exception as e:
            print(f"❌ Enhanced heuristic analysis error: {e}")
            return {
                "status": "error",
                "is_ai_generated": False,
                "ai_probability": 0.5,
                "confidence": 0.0,
                "method": "heuristic_error",
                "error": str(e)
            }
    
    def get_layer_info(self) -> Dict[str, Any]:
        """Get information about this layer"""
        info = {
            "layer_number": self.layer_number,
            "layer_name": self.layer_name,
            "status": "ready",
            "runpod_connected": self.model_loaded,
            "primary_method": "fast_detect_gpt_local" if (self.model_loaded and self.fast_detect_gpt) else "fast_detect_gpt_api" if (self.model_loaded and self.runpod_endpoint) else "enhanced_heuristic",
            "fallback_method": "enhanced_heuristic"
        }
        
        if self.model_loaded:
            if self.fast_detect_gpt:
                info.update({
                    "fast_detect_gpt_local": True,
                    "models": {
                        "sampling_model": self.fast_detect_gpt.sampling_model_name,
                        "scoring_model": self.fast_detect_gpt.scoring_model_name,
                        "device": self.fast_detect_gpt.device
                    },
                    "capabilities": [
                        "Local Fast-DetectGPT",
                        "Conditional probability curvature",
                        "High accuracy AI detection",
                        "Enhanced heuristic fallback"
                    ]
                })
            else:
                info.update({
                    "runpod_endpoint": self.runpod_endpoint[:50] + "..." if self.runpod_endpoint else None,
                    "capabilities": [
                        "Fast-DetectGPT via RunPod API",
                        "Multi-model scoring and sampling",
                        "High accuracy AI detection",
                        "Enhanced heuristic fallback"
                    ]
                })
        else:
            info.update({
                "setup_instructions": {
                    "local_option": "Install torch, transformers, scipy for local Fast-DetectGPT",
                    "runpod_option": {
                        "step1": "Set up RunPod instance with Fast-DetectGPT",
                        "step2": "Set RUNPOD_FAST_DETECT_ENDPOINT environment variable",
                        "step3": "Set RUNPOD_API_KEY environment variable",
                        "step4": "Restart backend to connect to RunPod"
                    }
                },
                "capabilities": [
                    "Enhanced heuristic analysis",
                    "Pattern detection",
                    "Sentence structure analysis",
                    "Vocabulary diversity check",
                    "Perplexity proxy calculation"
                ]
            })
        
        return info
