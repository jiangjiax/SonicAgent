import logging
import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv, set_key
from openai import OpenAI
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.prompts import WALLET_INTENT_PROMPT
from web3 import Web3
from src.constants.abi import ERC20_ABI
import requests
from datetime import datetime
from src.actions.wallet_actions import WalletActionHandler
from src.actions.token_info_actions import TokenInfoHandler
from src.actions.nft_info_actions import NFTInfoHandler

logger = logging.getLogger("connections.deepseek_connection")

class DeepSeekConnectionError(Exception):
    """Base exception for DeepSeek connection errors"""
    pass

class DeepSeekConfigurationError(DeepSeekConnectionError):
    """Raised when there are configuration/credential issues"""
    pass

class DeepSeekAPIError(DeepSeekConnectionError):
    """Raised when DeepSeek API requests fail"""
    pass

class DeepSeekConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._client = None

    @property
    def is_llm_provider(self) -> bool:
        return True

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate DeepSeek configuration from JSON"""
        required_fields = ["model"]
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")
            
        if not isinstance(config["model"], str):
            raise ValueError("model must be a string")
            
        return config

    def register_actions(self) -> None:
        """Register available DeepSeek actions"""
        self.actions = {
            "generate-text": Action(
                name="generate-text",
                parameters=[
                    ActionParameter("prompt", True, str, "The input prompt for text generation"),
                    ActionParameter("system_prompt", True, str, "System prompt to guide the model"),
                    ActionParameter("model", False, str, "Model to use for generation"),
                    ActionParameter("temperature", False, float, "Controls randomness in the response (0.0 to 1.0)")
                ],
                description="Generate text using DeepSeek models"
            ),
            "check-model": Action(
                name="check-model",
                parameters=[
                    ActionParameter("model", True, str, "Model name to check availability")
                ],
                description="Check if a specific model is available"
            ),
            "list-models": Action(
                name="list-models",
                parameters=[],
                description="List all available DeepSeek models"
            ),
            "get-hot-tokens": Action(
                name="get-hot-tokens",
                parameters=[
                    ActionParameter("limit", False, int, "Number of hot tokens to return")
                ],
                description="Get hot tokens on Sonic chain in last 24h"
            ),
            "get-new-tokens": Action(
                name="get-new-tokens",
                parameters=[
                    ActionParameter("limit", False, int, "Number of new tokens to return")
                ],
                description="Get newly listed tokens on Sonic chain"
            ),
            "get-supported-exchanges": Action(
                name="get-supported-exchanges",
                parameters=[],
                description="Get exchanges supporting Sonic chain tokens"
            ),
            "get-hot-tokens-json": Action(
                name="get-hot-tokens-json",
                parameters=[
                    ActionParameter("limit", False, int, "Number of hot tokens to return")
                ],
                description="Get hot tokens on Sonic chain in last 24h"
            ),
            "get-hot-nfts-json": Action(
                name="get-hot-nfts-json",
                parameters=[
                    ActionParameter("limit", False, int, "Number of hot NFTs to return"),
                    ActionParameter("base_url", False, str, "Base URL for PaintSwap collections")
                ],
                description="Get hot NFT collections in JSON format"
            ),
            "list-topics": Action(
                name="list-topics",
                parameters=[],
                description="List all available Allora prediction topics"
            ),
            "get-inference": Action(
                name="get-inference",
                parameters=[
                    ActionParameter("topic", True, str, "Topic name for prediction")
                ],
                description="Get prediction for a specific Allora topic"
            )
        }

    def _get_client(self) -> OpenAI:
        """Get or create DeepSeek client"""
        if not self._client:
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise DeepSeekConfigurationError("DeepSeek API key not found in environment")
            self._client = OpenAI(
                api_key=api_key,
                base_url="https://api.ppinfra.com/v3/openai"  # Updated base URL for PIPO
            )
        return self._client

    def configure(self) -> bool:
        """Sets up DeepSeek API authentication"""
        logger.info("\n🤖 DEEPSEEK API SETUP")

        if self.is_configured():
            logger.info("\nDeepSeek API is already configured.")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return True

        logger.info("\n📝 To get your DeepSeek API credentials:")
        logger.info("1. Go to https://platform.deepseek.com/settings")
        logger.info("2. Create a new API key")
        
        api_key = input("\nEnter your DeepSeek API key: ")

        try:
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')

            set_key('.env', 'DEEPSEEK_API_KEY', api_key)
            
            # Validate the API key by trying to list models
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.ppinfra.com/v3/openai"
            )
            client.models.list()

            logger.info("\n✅ DeepSeek API configuration successfully saved!")
            logger.info("Your API key has been stored in the .env file.")
            return True

        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False

    def is_configured(self, verbose = False) -> bool:
        """Check if DeepSeek API key is configured and valid"""
        try:
            load_dotenv()
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                return False

            client = OpenAI(
                api_key=api_key,
                base_url="https://api.ppinfra.com/v3/openai"
            )
            client.models.list()
            return True
            
        except Exception as e:
            if verbose:
                logger.debug(f"Configuration check failed: {e}")
            return False

    def generate_text(self, prompt: str = None, system_prompt: str = None, model: str = None, temperature: float = 0.5, **kwargs) -> str:
        """Generate text using DeepSeek models"""
        try:
            client = self._get_client()
            
            # 处理参数
            if isinstance(kwargs.get("params"), dict):
                params = kwargs["params"]
                prompt = params.get("prompt", prompt)
                system_prompt = params.get("system_prompt", system_prompt)
                temperature = params.get("temperature", temperature)
                connection_manager = params.get("connection_manager")
            else:
                connection_manager = kwargs.get("connection_manager")
            
            model = "deepseek/deepseek-v3"  # 强制使用 PIPO 的模型
            system_prompt = WALLET_INTENT_PROMPT  # 使用钱包操作系统提示

            # 构建请求
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "response_format": {"type": "json_object"}
            }
            
            completion = client.chat.completions.create(**request_data)    
            intent = completion.choices[0].message.content

            try:
                intent_data = json.loads(intent)
                action = intent_data.get("action")
                parameters = intent_data.get("parameters", {})
                
                if not connection_manager:
                    raise ValueError("Connection manager is required for operations")

                # 根据action类型调用相应的处理方法
                action_handlers = {
                    "get-balance": WalletActionHandler.handle_get_balance,
                    "get-token-by-ticker": WalletActionHandler.handle_get_token_by_ticker,
                    "transfer": WalletActionHandler.handle_transfer,
                    "get-hot-tokens": lambda p, cm: TokenInfoHandler.handle_hot_tokens(10),
                    "check-token-security": WalletActionHandler.handle_check_token_security,
                    "get-hot-nfts": lambda p, cm: NFTInfoHandler.handle_hot_nfts(10),
                    "get-nft-info": lambda p, cm: NFTInfoHandler.handle_nft_info(p.get("collection_address")),
                    "list-topics": lambda p, cm: self._handle_list_topics(cm),
                    "get-inference": lambda p, cm: self._handle_get_inference(p, cm)
                }

                if action in action_handlers:
                    logger.info(f"Executing action: {action} with parameters: {parameters}")
                    return action_handlers[action](parameters, connection_manager)
                else:
                    return str(intent)

            except json.JSONDecodeError:
                return str(intent)
            
        except Exception as e:
            raise DeepSeekAPIError(f"Text generation failed: {e}")

    def _handle_list_topics(self, connection_manager) -> str:
        """Handle list-topics action"""
        allora_connection = connection_manager.connections.get("allora")
        if not allora_connection:
            raise ValueError("Allora connection not found")
        
        try:
            topics = allora_connection.list_topics()
            if not topics:
                return "No prediction topics available"
            
            result = "Available Allora prediction topics:\n"
            for topic in topics:
                result += f"ID: {topic.topic_id} - {topic.topic_name}"
                if topic.description:
                    result += f": {topic.description}"
                result += f"\n   - Active: {topic.is_active}"
                result += f"\n   - Workers: {topic.worker_count}"
                result += f"\n   - Last Updated: {topic.updated_at}\n"
            
            result += "\nTo get a prediction, simply ask about any topic using its ID (e.g., 'What's the prediction for topic 22?' or 'Show me the forecast for ID 30')"
            return result
        except Exception as e:
            logger.error(f"Failed to list topics: {e}")
            return f"❌ Failed to list topics: {str(e)}"

    def _handle_get_inference(self, parameters: Dict[str, Any], connection_manager) -> str:
        """Handle get-inference action"""
        allora_connection = connection_manager.connections.get("allora")
        if not allora_connection:
            raise ValueError("Allora connection not found")
        
        topic_id = parameters.get("topic_id")
        if not topic_id:
            return "Please provide a topic ID for prediction. You can ask me to show you the list of available Allora prediction topics first."
        
        try:
            # 确保 topic_id 是整数
            topic_id = int(topic_id)
            
            # 获取主题信息以显示名称
            topics = allora_connection.list_topics()
            topic = next((t for t in topics if t.topic_id == topic_id), None)
            if not topic:
                return f"Topic ID {topic_id} not found. You can ask me to show you the list of available prediction topics."
            
            prediction = allora_connection.get_inference(topic_id)
            if not prediction:
                return f"No prediction available for topic: {topic.topic_name} (ID: {topic_id})"
            
            result = f"Prediction for {topic.topic_name} (ID: {topic_id}):\n"
            result += f"Forecast: {prediction['inference']}\n"
            if 'confidence' in prediction:
                result += f"Confidence: {prediction['confidence']}%\n"
            return result
        except ValueError:
            return "Invalid topic ID. Please provide a valid numeric topic ID."
        except Exception as e:
            logger.error(f"Failed to get prediction for topic {topic_id}: {e}")
            return f"❌ Failed to get prediction: {str(e)}"

    def check_model(self, model: str, **kwargs) -> bool:
        """Check if a specific model is available"""
        try:
            client = self._get_client()
            try:
                client.models.retrieve(model=model)
                return True
            except Exception:
                return False
        except Exception as e:
            raise DeepSeekAPIError(f"Model check failed: {e}")

    def list_models(self, **kwargs) -> None:
        """List all available DeepSeek models"""
        try:
            client = self._get_client()
            response = client.models.list().data
            
            fine_tuned_models = [
                model for model in response 
                if model.owned_by in ["organization", "user", "organization-owner"]
            ]

            logger.info("\nDEEPSEEK MODELS:")
            logger.info("1. deepseek-chat")
            logger.info("2. deepseek-coder")
            
            if fine_tuned_models:
                logger.info("\nFINE-TUNED MODELS:")
                for i, model in enumerate(fine_tuned_models):
                    logger.info(f"{i+1}. {model.id}")
                    
        except Exception as e:
            raise DeepSeekAPIError(f"Listing models failed: {e}")

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a DeepSeek action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        
        # 确保所有方法都能接收 connection_manager 参数
        return method(**kwargs)

    def get_hot_tokens_json(self, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """Get hot tokens in JSON format
        Args:
            limit: Number of tokens to return
            **kwargs: Additional arguments (e.g., connection_manager)
        """
        try:
            # 直接调用 get_hot_tokens 获取数据
            tokens = TokenInfoHandler.get_hot_tokens(limit)
            
            # 构建 JSON 响应
            return {
                "status": "success",
                "data": tokens
            }
        except Exception as e:
            logger.error(f"Failed to get hot tokens: {e}")
            return {
                "status": "error",
                "message": f"Failed to get hot tokens: {str(e)}"
            }

    def get_hot_nfts_json(self, limit: int = 10, base_url: str = "https://paintswap.io/sonic/collections/", **kwargs) -> Dict[str, Any]:
        """Get hot NFTs in JSON format
        Args:
            limit: Number of NFTs to return
            base_url: Base URL for PaintSwap collections
            **kwargs: Additional arguments (e.g., connection_manager)
        """
        try:
            # Call the NFTInfoHandler to get filtered hot NFTs with the base URL
            filtered_nfts = NFTInfoHandler.get_filtered_hot_nfts(limit, base_url)
            return {
                "status": "success",
                "data": filtered_nfts
            }
        except Exception as e:
            logger.error(f"Failed to get hot NFTs: {e}")
            return {
                "status": "error",
                "message": f"Failed to get hot NFTs: {str(e)}"
            }