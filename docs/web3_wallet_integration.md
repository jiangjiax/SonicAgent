# Web3 钱包集成设计文档

## 1. 概述

本文档概述了通过浏览器扩展（MetaMask）将自然语言处理与 Web3 钱包操作集成的架构和实现方法。

## 2. 系统组件

### 2.1 后端组件
- 自然语言处理（DeepSeek）
- FastAPI 服务器
- Web3 交易处理器
- 意图解析器

### 2.2 前端组件
- Web 界面
- MetaMask 集成
- 交易确认界面

## 3. 工作流设计

### 3.1 基本流程
1. 用户输入自然语言指令
2. 后端处理意图
3. 生成交易数据
4. 发送到前端
5. 前端触发 MetaMask
6. 用户确认交易
7. 交易执行
8. 状态更新

### 3.2 示例流程

    ```javascript
    // 示例用户输入
    "从我的钱包转账 0.1 ETH 到 0x123..."

    // 解析后的意图
    {
        "action": "transfer",
        "token": "ETH",
        "amount": "0.1",
        "to": "0x123...",
        "from": "user_wallet" // 将被实际地址替换
    }
    ```

## 4. API 端点

### 4.1 需要的新 FastAPI 端点

    ```python
    @app.post("/wallet/parse-intent")
    async def parse_wallet_intent(text: str):
        """将自然语言解析为钱包操作意图"""
        
    @app.post("/wallet/prepare-transaction")
    async def prepare_transaction(intent: WalletIntent):
        """为前端准备交易数据"""
        
    @app.post("/wallet/transaction-status")
    async def update_transaction_status(status: TransactionStatus):
        """更新交易执行状态"""
    ```

## 5. 意图识别系统

### 5.1 核心意图
- 查询余额
- 转账代币
- 查询交易
- 查看代币列表
- 获取 Gas 估算