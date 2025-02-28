from typing import Dict, Any, List
import logging
import requests
from datetime import datetime, timedelta
import time  # 导入 time 模块以处理缓存过期
from decimal import Decimal, getcontext

logger = logging.getLogger("actions.nft_info_actions")

class NFTInfoHandler:
    _cache = {
        'hot_nfts': None     # 存储热门 NFT 数据
    }
    CACHE_DURATION = timedelta(hours=1)  # 缓存有效期为1小时

    @staticmethod
    def handle_hot_nfts(limit: int = 10) -> str:
        """Handle get-hot-nfts action and return user-friendly text"""
        try:
            # Get hot NFT collections data
            hot_nfts = NFTInfoHandler.get_hot_nfts(limit)
            
            # Format output
            result = "🔥 Hot NFT Collections\n\n"
            for i, nft in enumerate(hot_nfts, 1):
                result += NFTInfoHandler._format_nft_info(i, nft)
            
            return result
        except Exception as e:
            logger.error(f"Failed to get hot NFTs: {e}")
            return "❌ Failed to get hot NFT collections. Please try again later."

    @staticmethod
    def get_hot_nfts(limit: int = 10, base_url: str = "https://paintswap.io/sonic/collections/") -> list:
        """Get hot NFT collections from PaintSwap API"""
        if NFTInfoHandler._cache['hot_nfts'] is not {} and NFTInfoHandler._cache['hot_nfts'] is not None:
            logger.info(NFTInfoHandler._cache['hot_nfts'])
            return NFTInfoHandler._cache['hot_nfts'][:limit]

        try:
            # If no cache, request new data
            response = requests.get(
                "https://api.paintswap.finance/v2/collections",
                params={"orderDirection": "desc", "numToFetch": limit, "orderBy": "volumeLast24Hours"}
            )
            response.raise_for_status()
            
            data = response.json()
            collections = data.get('collections', [])
            
            # Update cache
            NFTInfoHandler._cache['hot_nfts'] = collections
            
            # Add URL to each NFT collection
            for collection in collections:
                collection['url'] = f"{base_url}{collection['name']}"
            
            return collections[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get hot NFTs: {e}")
            if NFTInfoHandler._cache['hot_nfts'] is not {} and NFTInfoHandler._cache['hot_nfts'] is not None:
                logger.info("Returning cached data after API request failure")
                return NFTInfoHandler._cache['hot_nfts'][:limit]
            raise Exception(f"Failed to get hot NFTs: {e}")

    @staticmethod
    def get_filtered_hot_nfts(limit: int = 10, base_url: str = "https://paintswap.io/sonic/collections/") -> list:
        """Get filtered hot NFT collections for JSON response"""
        hot_nfts = NFTInfoHandler.get_hot_nfts(limit, base_url)
        
        # 选择性展示字段
        filtered_nfts = []
        for nft in hot_nfts:
            stats = nft.get('stats', {})
            filtered_nft = {
                'name': nft.get('name'),
                'address': nft.get('address'),
                'url': nft.get('url'),
                'thumbnail': nft.get('thumbnail'),
                'floor_price': NFTInfoHandler.convert_wei_to_sonic(float(stats.get('floor', 0))),  # 转换为 Sonic
                'created_at': nft.get('createdAt'),
                'active_sales': stats.get('activeSales'),
                'symbol': stats.get('symbol'),
                'website': nft.get('website'),
                'twitter': nft.get('twitter'),
                'isWhitelisted': stats.get('isWhitelisted'),
                'numOwners': stats.get('numOwners'),
                'totalNFTs': stats.get('totalNFTs'),
                'total_volume_traded': NFTInfoHandler.convert_wei_to_sonic(float(stats.get('totalVolumeTraded', 0))),  # 转换为 Sonic
                'volume_last_24_hours': NFTInfoHandler.convert_wei_to_sonic(float(stats.get('volumeLast24Hours', 0))),  # 转换为 Sonic
            }
            filtered_nfts.append(filtered_nft)
        
        return filtered_nfts

    @staticmethod
    def handle_nft_info(collection_address: str) -> str:
        """Handle get-nft-info action and return user-friendly text"""
        try:
            # Get NFT collection info
            nft_info = NFTInfoHandler.get_nft_info(collection_address)
            
            # Format output
            result = f"📊 NFT Collection Information\n\n"
            result += NFTInfoHandler._format_detailed_nft_info(nft_info.get('collection'))
            
            return result
        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            return f"❌ Failed to get NFT information for address {collection_address}. Please try again later."

    @staticmethod
    def get_nft_info(collection_address: str) -> Dict[str, Any]:
        """Get NFT collection info"""
        try:
            # 直接请求数据
            response = requests.get(f"https://api.paintswap.finance/v2/collections/{collection_address}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            raise Exception(f"Failed to get NFT info: {e}")

    @staticmethod
    def _format_nft_info(index: int, nft: Dict[str, Any]) -> str:
        """Format individual NFT collection information"""
        stats = nft.get('stats', {})
        
        # Keep original wei unit
        floor_price = stats.get('floor', '0')
        volume_24h = stats.get('volumeLast24Hours', '0')
        total_volume = stats.get('totalVolumeTraded', '0')
        isWhitelisted = stats.get('isWhitelisted')
        
        result = f"{index}. {nft.get('name', 'Unknown')}\n"
        result += f"   Address: {nft.get('address', 'N/A')}\n"
        result += f"   Creator: {nft.get('owner', 'N/A')}\n"
        
        if isWhitelisted is not None:
            result += f"   isWhitelisted: {'Yes' if isWhitelisted else 'No'}\n"

        # Add description
        if nft.get('description'):
            desc = nft['description']
            if len(desc) > 100:
                result += f"   Description: {desc[:100]}...\n"
            else:
                result += f"   Description: {desc}\n"
        
        # Add statistics with conversion to Sonic
        result += f"   Floor Price: {NFTInfoHandler.convert_wei_to_sonic(float(floor_price)):.6f} S\n"
        result += f"   24h Volume: {NFTInfoHandler.convert_wei_to_sonic(float(volume_24h)):.6f} S\n"
        result += f"   Total Volume: {NFTInfoHandler.convert_wei_to_sonic(float(total_volume)):.6f} S\n"

        active_sales = stats.get('activeSales')
        if active_sales:
            result += f"   Active Sales: {active_sales}\n"
        
        numOwners = stats.get('numOwners')
        if active_sales:
            result += f"   Num Owners: {numOwners}\n"

        totalNFTs = stats.get('totalNFTs')
        if active_sales:
            result += f"   Total NFTs: {totalNFTs}\n"
            
        # Add creation time
        created_at = nft.get('createdAt')
        if created_at:
            result += f"   Created At: {created_at}\n"
        
        # Add social media links
        if nft.get('website'):
            result += f"   Website: {nft['website']}\n"
        
        if nft.get('twitter'):
            result += f"   Twitter: {nft['twitter']}\n"
        
        result += "\n"
        return result

    @staticmethod
    def convert_wei_to_sonic(wei_amount: float) -> float:
        """Convert wei to Sonic tokens (S)
        1 S = 10^18 wei (EVM standard)
        """
        try:
            # 使用 Decimal 来保证精度
            return float(Decimal(wei_amount) / Decimal(1e18))
        except Exception as e:
            logger.error(f"Failed to convert wei to Sonic: {e}")
            return 0.0

    @staticmethod
    def _format_detailed_nft_info(nft: Dict[str, Any]) -> str:
        """Format detailed NFT collection information"""
        stats = nft.get('stats', {})
        
        # Keep original wei unit
        floor_price = stats.get('floor', '0')
        volume_24h = stats.get('volumeLast24Hours', '0')
        total_volume = stats.get('totalVolumeTraded', '0')
        
        result = f"Name: {nft.get('name', 'Unknown')}\n"
        result += f"Address: {nft.get('address', 'N/A')}\n"
        result += f"Creator: {nft.get('owner', 'N/A')}\n"
        
        # Add prices in Sonic
        result += f"Floor Price: {NFTInfoHandler.convert_wei_to_sonic(float(floor_price)):.6f} S\n"
        result += f"24h Volume: {NFTInfoHandler.convert_wei_to_sonic(float(volume_24h)):.6f} S\n"
        result += f"Total Volume: {NFTInfoHandler.convert_wei_to_sonic(float(total_volume)):.6f} S\n"
        
        active_sales = stats.get('activeSales')
        if active_sales:
            result += f"   Active Sales: {active_sales}\n"
        
        numOwners = stats.get('numOwners')
        if active_sales:
            result += f"   Num Owners: {numOwners}\n"

        totalNFTs = stats.get('totalNFTs')
        if active_sales:
            result += f"   Total NFTs: {totalNFTs}\n"

        # Add creation and update time
        created_at = nft.get('createdAt')
        if created_at:
            result += f"Created At: {created_at}\n"
        
        # Add links
        result += "\n🔗 Links:\n"
        
        if nft.get('website'):
            result += f"Website: {nft['website']}\n"
        
        if nft.get('twitter'):
            result += f"Twitter: {nft['twitter']}\n"
        
        if nft.get('discord'):
            result += f"Discord: {nft['discord']}\n"
        
        if nft.get('telegram'):
            result += f"Telegram: {nft['telegram']}\n"
        
        if nft.get('medium'):
            result += f"Medium: {nft['medium']}\n"
        
        if nft.get('reddit'):
            result += f"Reddit: {nft['reddit']}\n"
        
        return result