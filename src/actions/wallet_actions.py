from typing import Dict, Any, List
import logging
from web3 import Web3
from src.constants.abi import ERC20_ABI
import requests
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

logger = logging.getLogger("actions.wallet_actions")

class WalletActionHandler:
    @staticmethod
    def handle_get_balance(parameters: Dict[str, Any], connection_manager) -> str:
        """Handle get-balance action"""
        get_token_address = parameters.get("token_address")
        
        sonic_connection = connection_manager.connections.get("sonic")
        if not sonic_connection:
            raise ValueError("Sonic connection not found")
        
        if "token_name" not in parameters:
            return WalletActionHandler._get_all_balances(parameters["from_address"], sonic_connection)
            
        # 如果 token_name 是 "all"，查询所有代币余额
        if parameters["token_name"] == "all":
            return WalletActionHandler._get_all_balances(parameters["from_address"], sonic_connection)
        
        # 如果 token_name 不是 "S"，获取代币地址
        if parameters["token_name"] != "S":
            ticker = parameters.get("token_name")
            if not ticker:
                return "No token name provided"
            get_token_address = sonic_connection.get_token_by_ticker(ticker)
        
        # 查询单个代币余额
        result = sonic_connection.get_balance(
            address=parameters.get("from_address"),
            token_address=get_token_address
        )
        
        if result is not None:
            return f"Wallet {parameters['from_address']} {parameters['token_name']} balance: {result}"
        return None

    @staticmethod
    def _get_all_balances(address: str, sonic_connection) -> str:
        """Get all token balances for a given address"""
        try:
            logger.info(f"Fetching all token balances for address: {address}")
            
            # 获取地址的转账记录
            api_url = "https://api.sonicscan.org/api"
            logger.info(f"Making API request to: {api_url}")
            
            # 从环境变量中获取 API Key
            api_key = os.getenv("SONICSCAN_API_KEY")
            if not api_key:
                logger.error("SONICSCAN_API_KEY not found in .env file")
                return "❌ SONICSCAN_API_KEY not found in .env file"
            
            response = requests.get(
                api_url,
                params={
                    "module": "account",
                    "action": "tokentx",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "sort": "asc",
                    "apikey": api_key  # 添加 API Key
                }
            )
            response.raise_for_status()
            logger.info("API request successful")
            
            # 检查响应格式
            response_data = response.json()
            if not isinstance(response_data, dict):
                logger.error(f"Unexpected response format: {response_data}")
                return f"❌ Unexpected response format from API"
            
            # 提取所有代币地址
            token_transactions = response_data.get("result", [])
            if not isinstance(token_transactions, list):
                logger.error(f"Unexpected transactions format: {token_transactions}")
                return f"❌ Unexpected transactions format from API"
            
            logger.info(f"Found {len(token_transactions)} token transactions")
            
            token_addresses = set()
            for tx in token_transactions:
                if not isinstance(tx, dict):
                    logger.error(f"Unexpected transaction format: {tx}")
                    continue
                
                token_address = tx.get("contractAddress")
                if token_address:
                    token_addresses.add(token_address)
                    logger.debug(f"Found token address: {token_address}")
            
            logger.info(f"Extracted {len(token_addresses)} unique token addresses")
            
            # 查询每个代币的余额和名称
            balances = {}
            for token_address in token_addresses:
                logger.info(f"Fetching balance for token: {token_address}")
                balance = sonic_connection.get_balance(
                    address=address,
                    token_address=token_address
                )
                if balance is not None and balance > 0:
                    # 获取代币名称或符号
                    token_name = WalletActionHandler._get_token_name(sonic_connection, token_address)
                    balances[token_name or token_address] = balance
                    logger.info(f"{token_name or token_address} balance: {balance}")
                else:
                    logger.info(f"Token {token_address} has no balance or balance is zero")
            
            # 查询 S 代币的余额
            s_balance = sonic_connection.get_balance(address=address, token_address=None)
            if s_balance is not None and s_balance > 0:
                balances["S"] = s_balance
                logger.info(f"S balance: {s_balance}")
            
            # 格式化输出
            result = f"Wallet {address} balances:\n"
            for token_name, balance in balances.items():
                result += f"   {token_name}: {balance}\n"
            
            logger.info("Successfully fetched all token balances")
            return result
        except Exception as e:
            logger.error(f"Failed to get all balances: {e}")
            return f"❌ Failed to get all balances: {e}"

    @staticmethod
    def _get_token_name(sonic_connection, token_address: str) -> str:
        """Get token name or symbol by address"""
        try:
            contract = sonic_connection._web3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            # 先尝试获取代币名称
            try:
                token_name = contract.functions.name().call()
                return token_name
            except:
                # 如果获取名称失败，尝试获取代币符号
                token_symbol = contract.functions.symbol().call()
                return token_symbol
        except Exception as e:
            logger.error(f"Failed to get token name for {token_address}: {e}")
            return None

    @staticmethod
    def handle_get_token_by_ticker(parameters: Dict[str, Any], connection_manager) -> str:
        """Handle get-token-by-ticker action"""
        sonic_connection = connection_manager.connections.get("sonic")
        if not sonic_connection:
            raise ValueError("Sonic connection not found")
        
        ticker = parameters.get("token_name")
        if not ticker:
            return "No token name provided"
        
        token_address = sonic_connection.get_token_by_ticker(ticker)
        
        if token_address:
            return f"Token {ticker} address: {token_address}"
        return None

    @staticmethod
    def handle_transfer(parameters: Dict[str, Any], connection_manager) -> Dict[str, Any]:
        """Handle transfer action"""
        if not parameters.get("to_address"):
            return "Recipient address is required for transfer"
        if not parameters.get("amount"):
            return "Transfer amount is required"
        
        if "token_name" not in parameters:
            parameters["token_name"] = "S"
        
        sonic_connection = connection_manager.connections.get("sonic")
        if not sonic_connection:
            return "Sonic connection not found. Please check your configuration."
        
        token_address = parameters.get("token_address")
        if parameters["token_name"] != "S":
            token_address = sonic_connection.get_token_by_ticker(parameters["token_name"])
            if not token_address:
                return f"Could not find address for token {parameters['token_name']}"

        try:
            decimals = WalletActionHandler._get_token_decimals(sonic_connection, parameters["token_name"], token_address)
        except Exception as e:
            logger.error(f"Failed to get token decimals: {e}")
            decimals = 18  # 使用默认精度
        
        transaction_data = {
            "from": parameters["from_address"],
            "to": parameters["to_address"],
            "amount": parameters["amount"],
            "token_address": token_address,
            "token_name": parameters["token_name"],
            "decimals": decimals,
            "requires_signature": True
        }
        
        return {
            "action": "transfer",
            "transaction_data": transaction_data,
            "message": f"Please confirm transfer of {parameters['amount']} {parameters['token_name']} from your wallet address to {parameters['to_address']}"
        }

    @staticmethod
    def _get_token_decimals(sonic_connection, token_name: str, token_address: str) -> int:
        """Get token decimals"""
        if token_name == "S":
            return 18
        
        contract = sonic_connection._web3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        try:
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            return decimals
        except Exception as e:
            logger.error(f"Failed to get decimals for token {token_name}: {e}")
            logger.error(f"Full error details: {str(e)}")
            return 18 

    @staticmethod
    def handle_check_token_security(parameters: Dict[str, Any], connection_manager) -> Dict[str, Any]:
        """Handle check-token-security action"""
        try:
            token_address = parameters.get("token_address")
            if not token_address:
                return {"error": "No token address provided"}
            
            sonic_connection = connection_manager.connections.get("sonic")
            if not sonic_connection:
                return {"error": "Sonic connection not found"}
            
            # 获取合约安全检查结果
            security_checks = WalletActionHandler._check_contract_security(token_address, sonic_connection)
            
            # 计算安全评分
            score = 0
            risk_factors = [
                security_checks["is_upgradeable"],
                security_checks["has_blacklist"],
                security_checks["can_pause"],
                security_checks["hidden_mint"],
                security_checks["transfer_restrictions"],
                security_checks["suspicious_permissions"],
                security_checks["has_tax"],
                security_checks["can_mint"],
                security_checks["can_modify_lp"]
            ]
            
            # 计算得分
            for factor in risk_factors:
                if not factor:
                    score += 10
            
            # 确定风险等级
            if score >= 80:
                risk_level = "LOW"
            elif score >= 60:
                risk_level = "MEDIUM"
            elif score >= 40:
                risk_level = "HIGH"
            else:
                risk_level = "CRITICAL"
            
            # 返回结果
            return {
                **security_checks,
                "security_score": score,
                "risk_level": risk_level,
                "security_summary": f"Security Score: {score}/90, Risk Level: {risk_level}"
            }
        except Exception as e:
            logger.error(f"Failed to check token security: {e}")
            return {
                "error": f"Failed to check token security: {str(e)}",
                "risk_level": "UNKNOWN",
                "security_score": 0
            }

    @staticmethod
    def _check_contract_security(token_address: str, sonic_connection) -> Dict[str, Any]:
        """Check token contract security"""
        try:
            contract = sonic_connection._web3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )
            
            # 检查合约是否可升级
            is_upgradeable = False
            try:
                contract.functions.upgradeTo('0x0000000000000000000000000000000000000000').call()
                is_upgradeable = True
            except:
                pass

            # 检查是否有黑名单功能
            has_blacklist = False
            try:
                contract.functions.addToBlacklist('0x0000000000000000000000000000000000000000').call()
                has_blacklist = True
            except:
                pass

            # 检查是否可以暂停交易
            can_pause = False
            try:
                contract.functions.pause().call()
                can_pause = True
            except:
                pass

            # 检查是否有隐藏的增发功能
            hidden_mint = False
            try:
                contract.functions.mint('0x0000000000000000000000000000000000000000', 0).call()
                hidden_mint = True
            except:
                pass

            # 检查是否有可疑的转账限制
            transfer_restrictions = False
            try:
                contract.functions.transfer('0x0000000000000000000000000000000000000000', 0).call()
            except:
                transfer_restrictions = True

            # 检查是否有可疑的权限设置
            suspicious_permissions = False
            try:
                contract.functions.setOwner('0x0000000000000000000000000000000000000000').call()
                suspicious_permissions = True
            except:
                pass

            # 检查是否有交易税设置
            has_tax = False
            try:
                contract.functions.taxRate().call()
                has_tax = True
            except:
                pass

            # 检查是否有增发功能
            can_mint = False
            try:
                contract.functions.mint('0x0000000000000000000000000000000000000000', 0).call()
                can_mint = True
            except:
                pass

            # 检查是否有流动性池配对规则修改功能
            can_modify_lp = False
            try:
                contract.functions.setLpPair('0x0000000000000000000000000000000000000000').call()
                can_modify_lp = True
            except:
                pass

            return {
                "is_upgradeable": is_upgradeable,
                "has_blacklist": has_blacklist,
                "can_pause": can_pause,
                "hidden_mint": hidden_mint,
                "transfer_restrictions": transfer_restrictions,
                "suspicious_permissions": suspicious_permissions,
                "has_tax": has_tax,
                "can_mint": can_mint,
                "can_modify_lp": can_modify_lp
            }
        except Exception as e:
            logger.error(f"Failed to check contract security: {e}")
            return {
                "error": f"Failed to check contract security: {str(e)}",
                "risk_level": "UNKNOWN",
                "security_score": 0
            } 