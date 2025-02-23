from typing import Dict, Any, List
import logging
from web3 import Web3
from src.constants.abi import ERC20_ABI

logger = logging.getLogger("actions.wallet_actions")

class WalletActionHandler:
    @staticmethod
    def handle_get_balance(parameters: Dict[str, Any], connection_manager) -> str:
        """Handle get-balance action"""
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
        
        if result is not None:
            return f"Wallet {parameters['from_address']} {parameters['token_name']} balance: {result}"
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
    def handle_check_token_security(parameters: Dict[str, Any], connection_manager) -> str:
        """Handle check-token-security action and return user-friendly text in English"""
        sonic_connection = connection_manager.connections.get("sonic")
        if not sonic_connection:
            return "❌ Sonic connection not found. Please check your configuration."

        # If user provides token name but not address, try to find address by ticker
        token_name = parameters.get("token_name")
        token_address = parameters.get("token_address")
        
        if token_name and not token_address:
            token_address = sonic_connection.get_token_by_ticker(token_name)
            if not token_address:
                return f"❌ Could not find address for token {token_name}"

        # If user provides neither token name nor address, prompt user
        if not token_address:
            return "❌ Please provide either token name or token address to check security"

        # Get security check results
        security_report = WalletActionHandler._check_contract_security(sonic_connection, token_address)
        
        # If there's an error, return error message directly
        if "error" in security_report:
            return f"❌ {security_report['error']}"

        # Format security check results into user-friendly text
        result = f"🔍 Token Security Report\n\n"
        if token_name:
            result += f"Token Name: {token_name}\n"
        result += f"Contract Address: {token_address}\n"
        result += f"Risk Level: {security_report['risk_level'].upper()}\n\n"
        
        result += "Detailed Check Results:\n"
        result += f"• Is contract upgradeable: {'Yes' if security_report['is_upgradeable'] else 'No'}\n"
        result += f"• Has blacklist function: {'Yes' if security_report['has_blacklist'] else 'No'}\n"
        result += f"• Can pause transactions: {'Yes' if security_report['can_pause'] else 'No'}\n"
        result += f"• Has hidden mint function: {'Yes' if security_report['hidden_mint'] else 'No'}\n"
        result += f"• Has suspicious transfer restrictions: {'Yes' if security_report['transfer_restrictions'] else 'No'}\n"
        result += f"• Has suspicious permission settings: {'Yes' if security_report['suspicious_permissions'] else 'No'}\n"
        result += f"• Has tax: {'Yes' if security_report['has_tax'] else 'No'}\n"
        result += f"• Can mint: {'Yes' if security_report['can_mint'] else 'No'}\n"
        result += f"• Can modify liquidity pool: {'Yes' if security_report['can_modify_lp'] else 'No'}\n\n"
        
        # Provide suggestions based on risk level
        if security_report['risk_level'] == "high":
            result += "⚠️ Warning: This token has high risk! Please proceed with caution!\n"
        elif security_report['risk_level'] == "medium":
            result += "⚠️ Notice: This token has medium risk. Please evaluate carefully before proceeding.\n"
        else:
            result += "✅ This token has low risk, but still needs to be treated with caution.\n"
        
        return result

    @staticmethod
    def _check_contract_security(sonic_connection, token_address: str) -> Dict[str, Any]:
        """Perform actual contract security check"""
        try:
            # 获取合约实例
            contract = sonic_connection._web3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=ERC20_ABI
            )

            # 1. 检查合约是否可升级
            is_upgradeable = False
            try:
                # 检查是否有代理模式相关的函数
                implementation = contract.functions.implementation().call()
                is_upgradeable = implementation != '0x0000000000000000000000000000000000000000'
            except:
                pass

            # 2. 检查是否有黑名单功能
            has_blacklist = False
            try:
                # 检查是否有黑名单相关函数
                contract.functions.isBlacklisted('0x0000000000000000000000000000000000000000').call()
                has_blacklist = True
            except:
                pass

            # 3. 检查是否有暂停交易功能
            can_pause = False
            try:
                # 检查是否有暂停相关函数
                contract.functions.paused().call()
                can_pause = True
            except:
                pass

            # 4. 检查是否有隐藏的mint功能
            hidden_mint = False
            try:
                # 检查是否有mint相关函数
                contract.functions.mint('0x0000000000000000000000000000000000000000', 0).call()
                hidden_mint = True
            except:
                pass

            # 5. 检查是否有可疑的转账限制
            transfer_restrictions = False
            try:
                # 检查是否有转账限制相关函数
                contract.functions.maxTransferAmount().call()
                transfer_restrictions = True
            except:
                pass

            # 6. 检查是否有可疑的权限设置
            suspicious_permissions = False
            try:
                # 检查是否有owner或admin相关函数
                owner = contract.functions.owner().call()
                if owner != '0x0000000000000000000000000000000000000000':
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

            # 根据检查结果确定风险等级
            risk_factors = [
                is_upgradeable,
                has_blacklist,
                can_pause,
                hidden_mint,
                transfer_restrictions,
                suspicious_permissions,
                has_tax,
                can_mint,
                can_modify_lp
            ]
            risk_count = sum(risk_factors)
            
            if risk_count == 0:
                risk_level = "low"
            elif risk_count <= 2:
                risk_level = "medium"
            else:
                risk_level = "high"

            return {
                "is_upgradeable": is_upgradeable,
                "has_blacklist": has_blacklist,
                "can_pause": can_pause,
                "hidden_mint": hidden_mint,
                "transfer_restrictions": transfer_restrictions,
                "suspicious_permissions": suspicious_permissions,
                "risk_level": risk_level,
                "has_tax": has_tax,
                "can_mint": can_mint,
                "can_modify_lp": can_modify_lp
            }

        except Exception as e:
            logger.error(f"Failed to check contract security: {e}")
            return {
                "error": f"Failed to check contract security: {str(e)}",
                "risk_level": "unknown"
            } 