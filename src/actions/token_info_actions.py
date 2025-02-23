from typing import Dict, Any, List
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger("actions.token_info_actions")

class TokenInfoHandler:
    _cache = {
        'hot_tokens': None,
        'last_update': None
    }
    CACHE_DURATION = timedelta(hours=1)

    @staticmethod
    def handle_hot_tokens(limit: int = 5) -> str:
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
    def get_hot_tokens(limit: int = 5) -> list:
        """Get hot tokens on Sonic chain sorted by 24h volume"""
        # 检查缓存是否有效
        now = datetime.now()
        if (TokenInfoHandler._cache['hot_tokens'] is not None and 
            TokenInfoHandler._cache['last_update'] is not None and
            now - TokenInfoHandler._cache['last_update'] < TokenInfoHandler.CACHE_DURATION):
            logger.info("Returning cached hot tokens data")
            return TokenInfoHandler._cache['hot_tokens'][:limit]

        try:
            # 如果缓存无效，则请求新数据
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
                
                # 获取交易对信息
                pair_info = {
                    'pair_address': pair.get('pairAddress'),
                    'dex': pair.get('dexId'),
                    'volume_24h': volume_24h,
                    'liquidity_usd': liquidity,
                    'price_usd': pair.get('priceUsd'),
                    'price_native': pair.get('priceNative'),
                    'price_change_24h': pair.get('priceChange', {}).get('h24'),
                    'transactions_24h': pair.get('txns', {}).get('h24', {}),
                    'base_token': pair.get('baseToken', {}).get('symbol'),
                    'quote_token': pair.get('quoteToken', {}).get('symbol'),
                    'websites': pair.get('info', {}).get('websites', []),
                    'socials': pair.get('info', {}).get('socials', []),
                    'description': pair.get('info', {}).get('description')
                }
                
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
                        'market_cap': base.get('marketCap'),
                        'fdv': base.get('fdv'),
                        'pairs': []
                    }
                
                # 更新代币信息
                tokens_info[base_address]['total_volume_24h'] += volume_24h
                tokens_info[base_address]['max_liquidity_usd'] = max(
                    tokens_info[base_address]['max_liquidity_usd'],
                    liquidity
                )
                tokens_info[base_address]['pairs'].append(pair_info)
            
            # 按24小时交易量排序
            sorted_tokens = sorted(
                tokens_info.values(),
                key=lambda x: x['total_volume_24h'],
                reverse=True
            )
            
            # 更新缓存
            TokenInfoHandler._cache['hot_tokens'] = sorted_tokens
            TokenInfoHandler._cache['last_update'] = now
            
            return sorted_tokens[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get hot tokens: {e}")
            # 如果请求失败但有缓存数据，返回缓存的数据
            if TokenInfoHandler._cache['hot_tokens'] is not None:
                logger.info("Returning cached data after API request failure")
                return TokenInfoHandler._cache['hot_tokens'][:limit]
            raise Exception(f"Failed to get hot tokens: {e}")

    @staticmethod
    def _format_token_info(index: int, token: Dict[str, Any]) -> str:
        """Format individual token information in English"""
        result = f"{index}. {token['symbol']} ({token['name']})\n"
        result += f"   Contract Address: {token['address']}\n"
        result += f"   Total 24h Volume: ${float(token['total_volume_24h']):,.2f}\n"
        result += f"   Max Liquidity: ${float(token['max_liquidity_usd']):,.2f}\n"
        
        # Add market cap if available
        if token['market_cap'] is not None:
            try:
                market_cap = float(token['market_cap'])
                result += f"   Market Cap: ${market_cap:,.2f}\n"
            except (ValueError, TypeError):
                result += f"   Market Cap: ${token['market_cap']}\n"
        
        # Add FDV if available
        if token['fdv'] is not None:
            try:
                fdv = float(token['fdv'])
                result += f"   Fully Diluted Valuation: ${fdv:,.2f}\n"
            except (ValueError, TypeError):
                result += f"   Fully Diluted Valuation: ${token['fdv']}\n"
        
        # Add trading pairs
        result += TokenInfoHandler._format_pairs_info(token['pairs'])
        result += "\n"
        return result

    @staticmethod
    def _format_pairs_info(pairs: List[Dict[str, Any]]) -> str:
        """Format trading pairs information in English"""
        result = f"   Trading Pairs:\n"
        for pair in pairs:
            pair_name = f"{pair['base_token']}/{pair['quote_token']}"
            result += f"   - {pair_name} ({pair['dex']})\n"
            
            if pair['price_usd'] is not None:
                try:
                    result += f"     Price: ${float(pair['price_usd']):,.6f}\n"
                except (ValueError, TypeError):
                    result += f"     Price: ${pair['price_usd']}\n"
            
            if pair['price_change_24h'] is not None:
                try:
                    price_change = float(pair['price_change_24h'])
                    result += f"     24h Price Change: {price_change:+.2f}%\n"
                except (ValueError, TypeError):
                    result += f"     24h Price Change: {pair['price_change_24h']}%\n"
            
            try:
                result += f"     24h Volume: ${float(pair['volume_24h']):,.2f}\n"
                result += f"     Liquidity: ${float(pair['liquidity_usd']):,.2f}\n"
            except (ValueError, TypeError):
                result += f"     24h Volume: ${pair['volume_24h']}\n"
                result += f"     Liquidity: ${pair['liquidity_usd']}\n"
            
            txns = pair['transactions_24h']
            if txns:
                buys = txns.get('buys', 0)
                sells = txns.get('sells', 0)
                result += f"     24h Transactions: {buys} buys/{sells} sells\n"
            result += f"     Pair Address: {pair['pair_address']}\n"
            
            if pair.get('websites'):
                website_urls = [w['url'] for w in pair['websites'] if isinstance(w, dict) and 'url' in w]
                if website_urls:
                    result += f"     Websites: {', '.join(website_urls)}\n"
            
            if pair.get('socials'):
                result += "     Social Media:\n"
                for social in pair['socials']:
                    if isinstance(social, dict):
                        social_type = social.get('type', '').capitalize()
                        social_url = social.get('url', '')
                        if social_type and social_url:
                            result += f"      - {social_type}: {social_url}\n"
            
            if pair.get('description'):
                result += f"     Project Description: {pair['description']}\n"
        return result 