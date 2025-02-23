# 整理框架集成的连接及其用途：
---
1. Twitter
用途: 与 Twitter API 集成，用于发布推文、回复推文、点赞、读取时间线等。
常见操作:
发布推文
回复推文
读取用户时间线
---
2. Farcaster
用途: 与 Farcaster 协议集成，用于去中心化社交网络的交互。
常见操作:
发布 Cast（类似推文）
读取时间线
与其他用户互动
---
3. OpenAI
用途: 与 OpenAI 的 GPT 模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
代码生成
---
4. Anthropic
用途: 与 Anthropic 的 Claude 模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
5. XAI
用途: 与 XAI 的 Grok 模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
6. Together
用途: 与 Together AI 的模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
7. Solana
用途: 与 Solana 区块链集成，用于交易、质押、代币部署等。
常见操作:
发送交易
质押 SOL
部署代币
获取代币价格
---
8. EternalAI
用途: 与 Eternal AI 的模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
9. Ollama
用途: 与本地运行的 Ollama 模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
10. Goat
用途: 与 Goat 插件集成，用于加密货币数据获取和 ERC20 代币操作。
常见操作:
获取加密货币价格
查询 ERC20 代币信息
---
11. Groq
用途: 与 Groq 的模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
12. Hyperbolic
用途: 与 Hyperbolic 的模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
13. Galadriel
用途: 与 Galadriel 的模型集成，用于自然语言处理任务。
常见操作:
文本生成
聊天
翻译
---
14. Sonic
用途: 与 Sonic 网络集成，用于去中心化应用的交互。
常见操作:
发送交易
查询数据
---
15. Allora
用途: 与 Allora 预测网络集成，用于市场预测和数据推断。
常见操作:
获取预测结果
列出可用主题
---
16. EVM
用途: 与以太坊虚拟机（EVM）兼容的区块链集成，用于交易和智能合约交互。
常见操作:
发送交易
调用智能合约
---
17. Discord
用途: 与 Discord API 集成，用于消息发送、读取和互动。
常见操作:
发送消息
读取消息
添加表情
---
18. Deepseek
官方未集成，仿照官方的openai集成代码做了一个，跟openai的使用差不多。
---

# Allora 支持的主题列表

## 价格预测
- **ETH 价格预测**
  - ETH 5min Prediction (ID: 13)
  - ETH 10min Prediction (ID: 1)
  - ETH 20min Prediction (ID: 7)
  - ETH 8h Prediction (ID: 17)
  - ETH 24h Prediction (ID: 2)
  - ETH/USD 5min Price Prediction (ID: 30)
  - ETH/USD 8h Price Prediction (ID: 41)

- **BTC 价格预测**
  - BTC 5min Prediction (ID: 14)
  - BTC 10min Prediction (ID: 3)
  - BTC 24h Prediction (ID: 4)
  - BTC/USD 8h Price Prediction (ID: 42)

- **SOL 价格预测**
  - SOL 10min Prediction (ID: 5)
  - SOL 24h Prediction (ID: 6)
  - SOL/USD 5min Price Prediction (ID: 37)
  - SOL/USD 8h Price Prediction (ID: 38)

- **其他代币价格预测**
  - ARB 20min Prediction (ID: 9)
  - BNB 20min Prediction (ID: 8)
  - Memecoin 1h Prediction (ID: 10)
  - Virtual 5min Price Prediction (ID: 22)
  - Sekoia 5min Price Prediction (ID: 27)
  - G.A.M.E 5min Price Prediction (ID: 26)
  - VaderAI 5min Price Prediction (ID: 25)
  - Luna 5min Price Prediction (ID: 24)
  - Aixbt 5min Price Prediction (ID: 23)
  - Virtual/USDT 8h Price Prediction (ID: 31)
  - Aixbt/USDT 8h Price Prediction (ID: 32)
  - Luna/USDT 8h Price Prediction (ID: 33)
  - VaderAI/USDT 8h Price Prediction (ID: 34)
  - Game/USDT 8h Price Prediction (ID: 35)
  - Sekoia/USDT 8h Price Prediction (ID: 36)
  - SUI/USDT 30min Spot Return Prediction (ID: 45)

## 波动性预测
- **ETH 波动性预测**
  - ETH 5min Volatility Prediction (ID: 15)
  - ETH 8h Volatility Prediction (ID: 19)
  - ETH/USD 12h Volatility Prediction (ID: 28)
  - ETH/USD 8h Volatility Prediction (ID: 43)

- **BTC 波动性预测**
  - BTC 5min Volatility Prediction (ID: 16)
  - BTC 8h Volatility Prediction (ID: 20)
  - BTC/USD 8h Volatility Prediction (ID: 44)

- **SOL 波动性预测**
  - SOL/USD 5min Volatility Prediction (ID: 39)
  - SOL/USD 8h Volatility Prediction (ID: 40)

## 其他预测
- **Uniswap 交易量预测**
  - Arbitrum ETH/USDC Uniswap Pool 12h Volume Prediction (ID: 29)

- **特殊事件预测**
  - US Presidential Election 2024 - Winning Party (ID: 11) 

# 好的！以下是每个插件的 action 及其所需的参数和返回值的详细说明：
---
1. Coingecko 插件
Actions:
get-price
参数: token_id (代币 ID，如 bitcoin)
返回: {"price": float} (代币的当前价格)
get-market-data
参数: token_id (代币 ID)
返回: {"market_cap": float, "volume": float, "price_change_24h": float} (市场数据)
get-historical-price
参数: token_id (代币 ID), date (日期，格式为 YYYY-MM-DD)
返回: {"price": float} (历史价格)
get-token-list
参数: 无
返回: {"tokens": List[Dict]} (支持的代币列表)
---
2. DEXScreener 插件
Actions:
get-token-address
参数: ticker (代币符号，如 ETH)
返回: {"address": str} (代币地址)
get-pair-info
参数: pair_address (交易对地址)
返回: {"liquidity": float, "price": float, "volume": float} (交易对信息)
get-token-metrics
参数: token_address (代币地址)
返回: {"liquidity": float, "volume": float, "price": float} (代币指标)
search-token
参数: query (搜索关键词)
返回: {"tokens": List[Dict]} (匹配的代币列表)
---
3. 1inch 插件
Actions:
get-swap-rate
参数: token_in (输入代币地址), token_out (输出代币地址), amount (数量)
返回: {"rate": float, "estimated_gas": int} (兑换率和 Gas 估算)
execute-swap
参数: token_in (输入代币地址), token_out (输出代币地址), amount (数量), slippage (滑点百分比)
返回: {"tx_hash": str} (交易哈希)
get-liquidity-pools
参数: 无
返回: {"pools": List[Dict]} (流动性池列表)
get-gas-estimate
参数: token_in (输入代币地址), token_out (输出代币地址), amount (数量)
返回: {"gas_estimate": int} (Gas 估算)
---
4. Nansen 插件
Actions:
get-wallet-labels
参数: wallet_address (钱包地址)
返回: {"labels": List[str]} (钱包标签)
get-transaction-analysis
参数: tx_hash (交易哈希)
返回: {"analysis": Dict} (交易分析结果)
get-smart-contract-monitor
参数: contract_address (合约地址)
返回: {"activity": List[Dict]} (智能合约活动)
get-token-metrics
参数: token_address (代币地址)
返回: {"metrics": Dict} (代币链上指标)
---
5. OpenSea 插件
Actions:
get-nft-info
参数: nft_address (NFT 地址), token_id (NFT ID)
返回: {"name": str, "owner": str, "price": float} (NFT 信息)
buy-nft
参数: nft_address (NFT 地址), token_id (NFT ID), price (价格)
返回: {"tx_hash": str} (交易哈希)
sell-nft
参数: nft_address (NFT 地址), token_id (NFT ID), price (价格)
返回: {"tx_hash": str} (交易哈希)
get-collection-stats
参数: collection_slug (收藏品标识符)
返回: {"stats": Dict} (收藏品统计信息)
---
6. Rugcheck 插件
Actions:
audit-contract
参数: contract_address (合约地址)
返回: {"audit_report": Dict} (审计报告)
get-risk-score
参数: contract_address (合约地址)
返回: {"risk_score": float} (风险评分)
analyze-tokenomics
参数: contract_address (合约地址)
返回: {"tokenomics": Dict} (代币经济学分析)
check-rugpull
参数: contract_address (合约地址)
返回: {"is_rugpull": bool} (是否存在 Rugpull 风险)
---
7. Allora 插件
Actions:
get-data-feed
参数: feed_id (数据预言机 ID)
返回: {"data": Dict} (最新数据)
query-onchain-data
参数: query (查询条件)
返回: {"data": Dict} (链上数据)
validate-data
参数: data (待验证的数据)
返回: {"is_valid": bool} (数据是否有效)
submit-data
参数: data (提交的数据)
返回: {"submission_id": str} (提交 ID)
---