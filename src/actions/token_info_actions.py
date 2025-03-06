from typing import Dict, Any, List
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger("actions.token_info_actions")

class TokenInfoHandler:
    @staticmethod
    def handle_hot_tokens(limit: int = 10) -> str:
        """Handle get-hot-tokens action and return user-friendly text in English"""
        try:
            # 获取热门代币数据
            hot_tokens = TokenInfoHandler.get_hot_tokens(limit)
            
            # 格式化输出
            result = "🔥 Hot Tokens on Sonic Chain\n\n"
            for i, token in enumerate(hot_tokens, 1):
                result += TokenInfoHandler._format_token_info(i, token)
            
            return result
        except Exception as e:
            logger.error(f"Failed to get hot tokens: {e}")
            return "❌ Failed to get hot tokens. Please try again later."

    @staticmethod
    def get_hot_tokens(limit: int = 10) -> list:
        """Get hot tokens on Sonic chain sorted by 24h volume"""
        try:
            # 直接请求数据
            response = requests.get(
                "https://api.dexscreener.com/latest/dex/search",
                params={"q": "dyorswap wagmi shadow-exchange silverswap sonic"}
            )
            response.raise_for_status()
            
            data = response.json()
            pairs = data.get('pairs', [])
            
            # 过滤出Sonic链上的交易对
            sonic_pairs = [
                pair for pair in pairs 
                if pair.get("chainId") == "sonic"
            ]
            
            # 使用字典存储代币信息，键为地址
            tokens_info = {}
            
            # 先收集所有交易对信息
            for pair in sonic_pairs:
                # 安全地转换数值
                try:
                    volume_24h = float(pair.get('volume', {}).get('h24', 0) or 0)
                except (ValueError, TypeError):
                    volume_24h = 0
                    
                try:
                    liquidity = float(pair.get('liquidity', {}).get('usd', 0) or 0)
                except (ValueError, TypeError):
                    liquidity = 0
                
                # 处理 baseToken
                base = pair.get('baseToken', {})
                base_address = base.get('address')
                if base_address not in tokens_info:
                    tokens_info[base_address] = {
                        'address': base_address,
                        'name': base.get('name'),
                        'symbol': base.get('symbol'),
                        'total_volume_24h': 0,
                        'max_liquidity_usd': 0,
                        'priceUsd': pair.get('priceUsd'),
                        'priceNative': pair.get('priceNative'),
                        'chainId': pair.get('chainId'),
                        'url': pair.get('url'),
                        'websites': pair.get('info', {}).get('websites', []),
                        'socials': pair.get('info', {}).get('socials', []),
                        'imageUrl': pair.get('info', {}).get('imageUrl', []),
                        'marketCap': pair.get('marketCap'),
                        'priceChange_h24': pair.get('priceChange', {}).get('h24'),
                    }
                
                # 更新代币信息
                tokens_info[base_address]['total_volume_24h'] += volume_24h
                tokens_info[base_address]['max_liquidity_usd'] = max(
                    tokens_info[base_address]['max_liquidity_usd'],
                    liquidity
                )
            
            # 按24小时交易量排序
            sorted_tokens = sorted(
                tokens_info.values(),
                key=lambda x: x['total_volume_24h'],
                reverse=True
            )
            
            return sorted_tokens[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get hot tokens: {e}")
            raise Exception(f"Failed to get hot tokens: {e}")

    @staticmethod
    def _format_token_info(index: int, token: Dict[str, Any]) -> str:
        """Format individual token information in English"""
        result = f"{index}. {token['symbol']} ({token['name']})\n"
        result += f"   Contract Address: {token['address']}\n"
        result += f"   Total 24h Volume: ${float(token['total_volume_24h']):,.2f}\n"
        result += f"   Max Liquidity: ${float(token['max_liquidity_usd']):,.2f}\n"
        result += f"   Market Cap: ${float(token['marketCap']):,.2f}\n"
        result += f"   Price Change (24h): {token['priceChange_h24']}%\n"
        
        # Add price information if available
        if token.get('priceUsd') is not None:
            try:
                result += f"   Price (USD): ${float(token['priceUsd']):,.10f}\n"
            except (ValueError, TypeError):
                result += f"   Price (USD): ${token['priceUsd']}\n"
        
        if token.get('priceNative') is not None:
            try:
                result += f"   Price (Native): {float(token['priceNative']):,.10f}\n"
            except (ValueError, TypeError):
                result += f"   Price (Native): {token['priceNative']}\n"
        
        # Add chain and URL information
        if token.get('chainId'):
            result += f"   Chain: {token['chainId']}\n"
        if token.get('url'):
            result += f"   URL: {token['url']}\n"
        
        # Add websites if available
        if token.get('websites'):
            website_urls = [w['url'] for w in token['websites'] if isinstance(w, dict) and 'url' in w]
            if website_urls:
                result += f"   Websites: {', '.join(website_urls)}\n"
        
        # Add socials if available
        if token.get('socials'):
            result += "   Social Media:\n"
            for social in token['socials']:
                if isinstance(social, dict):
                    social_type = social.get('type', '').capitalize()
                    social_url = social.get('url', '')
                    if social_type and social_url:
                        result += f"    - {social_type}: {social_url}\n"
        
        result += "\n"
        return result 