SONIC_NETWORKS = {
    "mainnet": {
        "rpc_url": "https://rpc.soniclabs.com",
        "scanner_url": "https://sonicscan.org"
    },
    "testnet": {
        "rpc_url": "https://rpc.blaze.soniclabs.com",
        "scanner_url": "https://testnet.sonicscan.org"
    },
    "custom": {
        "rpc_url": "placeholder",
        "scanner_url": "https://sonicscan.org"
        }
    }

EVM_NETWORKS = {
    "ethereum": {
        "rpc_url": "https://ethereum-rpc.publicnode.com",
        "scanner_url": "etherscan.io",
        "chain_id": 1
    },
    "sepolia": {
        "rpc_url": "https://eth-sepolia.g.alchemy.com/v2/hy4m6PD3-Inxyi7H1oiWubV_EFy9cYeF",  # 或其他 Sepolia RPC
        "scanner_url": "sepolia.etherscan.io",
        "chain_id": 11155111
    },
    "base": {
        "rpc_url": "https://mainnet.base.org",
        "scanner_url": "basescan.org",
        "chain_id": 8453
    },
    "polygon": {
        "rpc_url": "https://polygon-rpc.com",
        "scanner_url": "polygonscan.com",
        "chain_id": 137
    }
}