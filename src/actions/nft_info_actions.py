from typing import Dict, Any, List
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger("actions.nft_info_actions")

class NFTInfoHandler:
    _cache = {
        'hot_nfts': None,
        'nft_info': {},
        'last_update': None
    }
    CACHE_DURATION = timedelta(hours=1)

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
    def get_hot_nfts(limit: int = 10) -> list:
        """Get hot NFT collections from PaintSwap API"""
        # Check if cache is valid
        now = datetime.now()
        if (NFTInfoHandler._cache['hot_nfts'] is not None and 
            NFTInfoHandler._cache['last_update'] is not None and
            now - NFTInfoHandler._cache['last_update'] < NFTInfoHandler.CACHE_DURATION):
            logger.info("Returning cached hot NFTs data")
            return NFTInfoHandler._cache['hot_nfts'][:limit]

        try:
            # If cache is invalid, request new data
            response = requests.get(
                "https://api.paintswap.finance/v2/collections",
                params={"orderDirection": "desc", "numToFetch": limit, "orderBy": "volumeLast24Hours"}
            )
            response.raise_for_status()
            
            data = response.json()
            collections = data.get('collections', [])
            
            # Update cache
            NFTInfoHandler._cache['hot_nfts'] = collections
            NFTInfoHandler._cache['last_update'] = now
            
            return collections[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get hot NFTs: {e}")
            # If request fails but cache data exists, return cached data
            if NFTInfoHandler._cache['hot_nfts'] is not None:
                logger.info("Returning cached data after API request failure")
                return NFTInfoHandler._cache['hot_nfts'][:limit]
            raise Exception(f"Failed to get hot NFTs: {e}")

    @staticmethod
    def handle_nft_info(collection_address: str) -> str:
        """Handle get-nft-info action and return user-friendly text"""
        try:
            # Get NFT collection info
            nft_info = NFTInfoHandler.get_nft_info(collection_address)
            
            # Format output
            result = f"📊 NFT Collection Information\n\n"
            result += NFTInfoHandler._format_detailed_nft_info(nft_info)
            
            return result
        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            return f"❌ Failed to get NFT information for address {collection_address}. Please try again later."

    @staticmethod
    def get_nft_info(collection_address: str) -> Dict[str, Any]:
        """Get NFT collection info by address from PaintSwap API"""
        # Check if cache is valid
        now = datetime.now()
        if (collection_address in NFTInfoHandler._cache['nft_info'] and 
            NFTInfoHandler._cache['last_update'] is not None and
            now - NFTInfoHandler._cache['last_update'] < NFTInfoHandler.CACHE_DURATION):
            logger.info(f"Returning cached NFT info for {collection_address}")
            return NFTInfoHandler._cache['nft_info'][collection_address]

        try:
            # If cache is invalid, request new data
            response = requests.get(
                f"https://api.paintswap.finance/v2/collections/{collection_address}"
            )
            response.raise_for_status()
            
            data = response.json()
            collection = data.get('collection', {})
            
            # Update cache
            NFTInfoHandler._cache['nft_info'][collection_address] = collection
            NFTInfoHandler._cache['last_update'] = now
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get NFT info for {collection_address}: {e}")
            # If request fails but cache data exists, return cached data
            if collection_address in NFTInfoHandler._cache['nft_info']:
                logger.info("Returning cached data after API request failure")
                return NFTInfoHandler._cache['nft_info'][collection_address]
            raise Exception(f"Failed to get NFT info: {e}")

    @staticmethod
    def _format_nft_info(index: int, nft: Dict[str, Any]) -> str:
        """Format individual NFT collection information"""
        stats = nft.get('stats', {})
        
        # Keep original wei unit
        floor_price = stats.get('floor', '0')
        volume_24h = stats.get('volumeLast24Hours', '0')
        volume_7d = stats.get('volumeLast7Days', '0')
        total_volume = stats.get('totalVolumeTraded', '0')
        highest_sale = stats.get('highestSale', '0')
        
        result = f"{index}. {nft.get('name', 'Unknown')}\n"
        result += f"   Address: {nft.get('address', 'N/A')}\n"
        result += f"   Creator: {nft.get('owner', 'N/A')}\n"
        
        # Add symbol
        symbol = stats.get('symbol')
        if symbol:
            result += f"   Symbol: {symbol}\n"
        
        # Add standard and chain ID
        standard = nft.get('standard')
        if standard:
            result += f"   Standard: ERC-{standard}\n"
        
        chain_id = nft.get('chainId')
        if chain_id:
            result += f"   Chain ID: {chain_id}\n"
        
        # Add verification status
        verified = nft.get('verified')
        if verified is not None:
            result += f"   Verified: {'Yes' if verified else 'No'}\n"
        
        # Add NSFW flag
        nsfw = nft.get('nsfw')
        if nsfw is not None:
            result += f"   NSFW: {'Yes' if nsfw else 'No'}\n"
        
        # Add mint price
        mint_price_low = nft.get('mintPriceLow')
        mint_price_high = nft.get('mintPriceHigh')
        if mint_price_low is not None and mint_price_high is not None:
            if mint_price_low == mint_price_high:
                result += f"   Mint Price: {mint_price_low} wei\n"
            else:
                result += f"   Mint Price Range: {mint_price_low} - {mint_price_high} wei\n"
        
        # Add description
        if nft.get('description'):
            desc = nft['description']
            if len(desc) > 100:
                result += f"   Description: {desc[:100]}...\n"
            else:
                result += f"   Description: {desc}\n"
        
        # Add statistics
        result += f"   Floor Price: {floor_price} wei\n"
        result += f"   24h Volume: {volume_24h} wei\n"
        result += f"   7d Volume: {volume_7d} wei\n"
        result += f"   Total Volume: {total_volume} wei\n"
        
        if highest_sale and highest_sale != '0':
            result += f"   Highest Sale: {highest_sale} wei\n"
        
        total_supply = stats.get('totalMinted')
        if total_supply:
            result += f"   Total Supply: {total_supply}\n"
        
        owners = stats.get('numOwners')
        if owners:
            result += f"   Unique Owners: {owners}\n"
        
        active_sales = stats.get('activeSales')
        if active_sales:
            result += f"   Active Sales: {active_sales}\n"
        
        total_trades = stats.get('totalTrades')
        if total_trades:
            result += f"   Total Trades: {total_trades}\n"
        
        # Add creation time
        created_at = nft.get('createdAt')
        if created_at:
            result += f"   Created At: {created_at}\n"
        
        # Add social media links
        if nft.get('website'):
            result += f"   Website: {nft['website']}\n"
        
        if nft.get('twitter'):
            result += f"   Twitter: {nft['twitter']}\n"
        
        if nft.get('discord'):
            result += f"   Discord: {nft['discord']}\n"
        
        if nft.get('telegram'):
            result += f"   Telegram: {nft['telegram']}\n"
        
        result += "\n"
        return result

    @staticmethod
    def _format_detailed_nft_info(nft: Dict[str, Any]) -> str:
        """Format detailed NFT collection information"""
        stats = nft.get('stats', {})
        
        # Keep original wei unit
        floor_price = stats.get('floor', '0')
        volume_24h = stats.get('volumeLast24Hours', '0')
        volume_7d = stats.get('volumeLast7Days', '0')
        total_volume = stats.get('totalVolumeTraded', '0')
        highest_sale = stats.get('highestSale', '0')
        
        result = f"Name: {nft.get('name', 'Unknown')}\n"
        result += f"Address: {nft.get('address', 'N/A')}\n"
        result += f"Creator: {nft.get('owner', 'N/A')}\n"
        
        # Add symbol
        symbol = stats.get('symbol')
        if symbol:
            result += f"Symbol: {symbol}\n"
        
        # Add standard and chain ID
        standard = nft.get('standard')
        if standard:
            result += f"Standard: ERC-{standard}\n"
        
        chain_id = nft.get('chainId')
        if chain_id:
            result += f"Chain ID: {chain_id}\n"
        
        # Add verification status
        verified = nft.get('verified')
        if verified is not None:
            result += f"Verified: {'Yes' if verified else 'No'}\n"
        
        # Add NSFW flag
        nsfw = nft.get('nsfw')
        if nsfw is not None:
            result += f"NSFW: {'Yes' if nsfw else 'No'}\n"
        
        # Add mint price
        mint_price_low = nft.get('mintPriceLow')
        mint_price_high = nft.get('mintPriceHigh')
        if mint_price_low is not None and mint_price_high is not None:
            if mint_price_low == mint_price_high:
                result += f"Mint Price: {mint_price_low} wei\n"
            else:
                result += f"Mint Price Range: {mint_price_low} - {mint_price_high} wei\n"
        
        # Add description
        if nft.get('description'):
            result += f"\nDescription: {nft['description'][:200]}...\n" if len(nft['description']) > 200 else f"\nDescription: {nft['description']}\n"
        
        # Add statistics
        result += "\n📈 Statistics:\n"
        result += f"Floor Price: {floor_price} wei\n"
        
        total_supply = stats.get('totalMinted')
        if total_supply:
            result += f"Total Supply: {total_supply}\n"
        
        owners = stats.get('numOwners')
        if owners:
            result += f"Unique Owners: {owners}\n"
        
        active_sales = stats.get('activeSales')
        if active_sales:
            result += f"Active Sales: {active_sales}\n"
        
        total_trades = stats.get('totalTrades')
        if total_trades:
            result += f"Total Trades: {total_trades}\n"
        
        # Add volume information
        result += f"24h Volume: {volume_24h} wei\n"
        result += f"7d Volume: {volume_7d} wei\n"
        result += f"Total Volume: {total_volume} wei\n"
        
        if highest_sale and highest_sale != '0':
            result += f"Highest Sale: {highest_sale} wei\n"
        
        # Add creation and update time
        created_at = nft.get('createdAt')
        if created_at:
            result += f"Created At: {created_at}\n"
        
        updated_at = nft.get('updatedAt')
        if updated_at:
            result += f"Updated At: {updated_at}\n"
        
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
        
        # Add image links
        result += "\n🖼️ Images:\n"
        
        if nft.get('poster'):
            result += f"Poster: {nft['poster']}\n"
        
        if nft.get('banner'):
            result += f"Banner: {nft['banner']}\n"
        
        if nft.get('thumbnail'):
            result += f"Thumbnail: {nft['thumbnail']}\n"
        
        if nft.get('marketing'):
            result += f"Marketing: {nft['marketing']}\n"
        
        return result

    @staticmethod
    def handle_hot_nfts_json(limit: int = 10) -> Dict[str, Any]:
        """Handle get-hot-nfts action and return JSON format data"""
        try:
            # Get hot NFT collections
            hot_nfts = NFTInfoHandler.get_hot_nfts(limit)
            
            # Return JSON response
            return {
                "status": "success",
                "data": hot_nfts
            }
        except Exception as e:
            logger.error(f"Failed to get hot NFTs: {e}")
            return {
                "status": "error",
                "message": f"Failed to get hot NFTs: {str(e)}"
            }
    
    @staticmethod
    def handle_nft_info_json(collection_address: str) -> Dict[str, Any]:
        """Handle get-nft-info action and return JSON format data"""
        try:
            # Get NFT collection info
            nft_info = NFTInfoHandler.get_nft_info(collection_address)
            
            # Return JSON response
            return {
                "status": "success",
                "data": nft_info
            }
        except Exception as e:
            logger.error(f"Failed to get NFT info: {e}")
            return {
                "status": "error",
                "message": f"Failed to get NFT info: {str(e)}"
            } 