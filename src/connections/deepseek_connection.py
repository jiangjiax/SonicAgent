import logging
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from openai import OpenAI
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.prompts import WALLET_INTENT_PROMPT

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
                    ActionParameter("model", False, str, "Model to use for generation")
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

    def generate_text(self, prompt: str = None, system_prompt: str = None, model: str = None, **kwargs) -> str:
        """Generate text using DeepSeek models"""
        try:
            client = self._get_client()
            
            # 如果参数是通过字典传入的，从kwargs中获取
            if isinstance(kwargs.get("params"), dict):
                params = kwargs["params"]
                prompt = params.get("prompt", prompt)
                system_prompt = params.get("system_prompt", system_prompt)
                connection_manager = params.get("connection_manager")
            else:
                connection_manager = kwargs.get("connection_manager")
            
            # 强制使用 PIPO 的模型
            model = "deepseek/deepseek-v3"
            
            # 使用钱包操作系统提示
            system_prompt = WALLET_INTENT_PROMPT

            # 构建请求
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "response_format": {"type": "json_object"}
            }
            
            completion = client.chat.completions.create(**request_data)    
            intent = completion.choices[0].message.content

            # print(f"\nIntent: {intent}")

            # 解析意图并执行相应操作
            try:
                # Try to parse as JSON for wallet operations
                try:
                    intent_data = json.loads(intent)
                    # If successfully parsed as JSON, it's a wallet operation
                    action = intent_data.get("action")
                    print(f"\nAction: {action}")
                    parameters = intent_data.get("parameters", {})

                    if not connection_manager:
                        raise ValueError("Connection manager is required for wallet operations")

                    # Handle balance query
                    if action == "get-balance":
                        get_token_address = parameters.get("token_address")
                        if "token_name" not in parameters:
                            parameters["token_name"] = "S"
                        if parameters["token_name"] != "S":
                            sonic_connection = connection_manager.connections.get("sonic")
                            if not sonic_connection:
                                raise ValueError("Sonic connection not found")
                                
                            ticker = parameters.get("token_name")
                            if not ticker:
                                return "No token name provided"
                            get_token_address = sonic_connection.get_token_by_ticker(ticker)

                        sonic_connection = connection_manager.connections.get("sonic")
                        if not sonic_connection:
                            raise ValueError("Sonic connection not found")
                            
                        result = sonic_connection.get_balance(
                            address=parameters.get("from_address"),
                            token_address=get_token_address
                        )
                        
                        # token_name有可能不存在，要判断一下
                        if "token_name" not in parameters:
                            parameters["token_name"] = "S"
                        if result is not None:
                            return f"Wallet {parameters['from_address']} {parameters['token_name']} balance: {result}"
                        else:
                            return f"Failed to get balance for wallet {parameters['from_address']}"

                    # Add new handler for get-token-by-ticker
                    elif action == "get-token-by-ticker":
                        sonic_connection = connection_manager.connections.get("sonic")
                        if not sonic_connection:
                            raise ValueError("Sonic connection not found")
                            
                        ticker = parameters.get("token_name")
                        if not ticker:
                            return "No token name provided"
                            
                        token_address = sonic_connection.get_token_by_ticker(ticker)
                        
                        if token_address:
                            return f"Token {ticker} address: {token_address}"
                        else:
                            return f"Could not find address for token {ticker}"

                    # Add transfer handler in generate_text method after get-token-by-ticker handler
                    elif action == "transfer":
                        print(f"\nTransfer action: {parameters}")
                        # 检查必要参数
                        if not parameters.get("to_address"):
                            return "Recipient address is required for transfer"
                        if not parameters.get("amount"):
                            return "Transfer amount is required"
                        
                        # 获取或设置代币信息
                        if "token_name" not in parameters:
                            parameters["token_name"] = "S"
                        
                        # 如果不是原生代币，需要获取代币地址
                        token_address = parameters.get("token_address")
                        if parameters["token_name"] != "S":
                            sonic_connection = connection_manager.connections.get("sonic")
                            if not sonic_connection:
                                raise ValueError("Sonic connection not found")
                                
                            token_address = sonic_connection.get_token_by_ticker(parameters["token_name"])
                            if not token_address:
                                return f"Could not find address for token {parameters['token_name']}"
                        
                        # 准备交易数据
                        transaction_data = {
                            "from": parameters["from_address"],
                            "to": parameters["to_address"],
                            "amount": parameters["amount"],
                            "token_address": token_address,
                            "token_name": parameters["token_name"],
                            "requires_signature": True
                        }
                        
                        # 返回交易数据供前端处理
                        return {
                            "action": "transfer",
                            "transaction_data": transaction_data,
                            "message": f"Please confirm transfer of {parameters['amount']} {parameters['token_name']} from {parameters['from_address']} to {parameters['to_address']}"
                        }

                    # For other wallet operations, return the intent JSON
                    return intent

                except json.JSONDecodeError:
                    # If not valid JSON, it's a non-wallet query response
                    return intent

            except Exception as e:
                print(f"\nText generation failed with error: {str(e)}")
                print(f"Error type: {type(e)}")
                raise DeepSeekAPIError(f"Text generation failed: {e}")
            
        except Exception as e:
            print(f"\nText generation failed with error: {str(e)}")
            print(f"Error type: {type(e)}")
            raise DeepSeekAPIError(f"Text generation failed: {e}")

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
        return method(**kwargs) 