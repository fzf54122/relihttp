---
title: "🚀 relihttp：面向生产、默认可靠的 Python HTTP 客户端"
date: 2026-02-03
categories: [Python, HTTP 客户端]
tags: [requests, 重试机制, 超时控制, 限流, 熔断器]
pin: true
description: "🎯 基于 requests 构建的轻量级 HTTP 客户端，默认内置可靠性特性：超时、重试、限流、结构化日志和熔断器！"
---

<style>
  img {
    max-width: 100%;
    height: auto;
  }
</style>

<div align="center">
  <img src="./assets/img/relihttp-icon.svg" alt="relihttp Logo" width="120" height="120" style="margin-bottom: 15px;"/>
</div>

- 📁 **GitHub**：https://github.com/fzf54122/relihttp/

---

## 背景：为什么需要 relihttp
<div align="center">
  <img src="./assets/img/relihttp.png" alt="relihttp Logo" width="792" height="397" >
</div>

在现代应用开发中，HTTP 客户端是连接外部服务的重要桥梁。然而，开发一个可靠的 HTTP 客户端往往需要处理诸多细节：

- ⏱️ **超时控制**：防止请求无限等待
- 🔄 **重试机制**：处理网络波动和瞬时错误
- 🚦 **限流保护**：避免对外部服务造成压力
- 📝 **日志监控**：追踪请求状态和性能
- 🛡️ **熔断保护**：防止级联故障

传统的 `requests` 库虽然易用，但需要开发者手动添加这些可靠性特性。每次开发新项目时，我都发现自己在重复编写相似的代码：

🤦‍♂️ **重复劳动**：为每个项目实现重试、超时和日志
😫 **不一致性**：不同项目的可靠性策略各不相同
💥 **隐藏风险**：遗漏某些边界情况导致生产故障

基于这些痛点，我开发了 **relihttp** - 一个默认可靠的 HTTP 客户端，将常见的可靠性特性封装为可配置的策略，让开发者能够专注于业务逻辑而非底层细节。

---

## 设计目标与边界

**目标**：
- 🎯 提供默认可靠的 HTTP 客户端体验
- ⚡ 保持与 `requests` API 兼容，降低学习成本
- 🔧 采用策略式设计，支持灵活扩展和定制
- 📊 内置结构化日志，提升可观测性
- 🛡️ 包含完整的可靠性特性：超时、重试、限流、熔断器

**不做（至少现在不做）**：
- ❌ 不替代 `requests` 的核心功能
- ❌ 不提供完整的 HTTP/2 支持
- ❌ 不实现复杂的负载均衡

---

## 🎯 relihttp vs requests：核心差异

relihttp 不是要替代 `requests`，而是要在其基础上提供默认的可靠性特性。以下是两者的核心差异对比：

| 特性 | requests | relihttp |
|------|----------|----------|
| **默认超时** | ❌ 无默认超时，可能导致请求无限等待 | ✅ 默认 3 秒超时 |
| **自动重试** | ❌ 无内置重试机制 | ✅ 安全方法自动重试，可配置 |
| **限流保护** | ❌ 无内置限流 | ✅ 令牌桶算法限流，支持两种模式 |
| **熔断机制** | ❌ 无熔断保护 | ✅ 三级状态熔断保护，防止级联故障 |
| **结构化日志** | ❌ 基本日志 | ✅ 完整的请求上下文日志，支持监控 |
| **策略式设计** | ❌ 单一实现 | ✅ 可插拔策略，支持灵活扩展 |
| **异步支持** | ❌ 同步客户端 | ✅ 完整的异步客户端 API |
| **使用复杂度** | 🟢 简单，API 直观 | 🟢 与 requests 兼容，学习成本低 |
| **可靠性** | 🟠 需手动实现 | ✅ 默认可靠，开箱即用 |

### 📖 代码对比示例

**使用 requests 实现可靠请求（手动）**：
```python
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

for attempt in range(3):
    try:
        logging.info(f"Attempt {attempt+1}: GET https://api.example.com/users")
        response = requests.get(
            "https://api.example.com/users",
            timeout=3.0  # 需手动设置
        )
        if response.status_code in [500, 502, 503, 504, 429]:
            logging.warning(f"Retryable error: {response.status_code}")
            time.sleep(2 ** attempt * 0.5)  # 手动实现退避
            continue
        response.raise_for_status()
        break
    except requests.exceptions.Timeout:
        logging.warning("Request timed out")
        time.sleep(2 ** attempt * 0.5)
        continue
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        break
```

**使用 relihttp 实现可靠请求（自动）**：
```python
from relihttp import Client

client = Client(
    timeout=3.0,  # 全局配置
    retry="safe",  # 自动重试安全方法
    max_retries=3  # 最大重试次数
)

# 一行代码实现自动重试、超时控制和日志记录
response = client.get("https://api.example.com/users")
```

---

## 🌍 真实世界应用场景

relihttp 适用于各种需要可靠 HTTP 通信的场景，以下是几个典型案例：

### 1. 🛒 电商支付系统

在电商支付场景中，可靠性至关重要：
- **超时控制**：确保支付请求在合理时间内完成，避免用户等待
- **限流保护**：防止高峰期请求量过大导致支付网关崩溃
- **安全重试**：对于幂等操作（如查询订单状态）自动重试
- **熔断机制**：当支付网关异常时，快速失败并保护系统

```python
# 支付服务客户端配置
payment_client = Client(
    base_url="https://payment-gateway.example.com",
    timeout=2.0,  # 支付请求超时更严格
    retry="safe",  # 仅重试安全方法
    max_retries=2,  # 最小化重试次数避免重复支付
    rate_limit=100,  # 限制支付请求速率
    circuit_breaker=True,  # 熔断保护
)

# 订单状态查询（安全重试）
order_status = payment_client.get(f"/orders/{order_id}/status").json()

# 支付请求（最小重试）
payment_result = payment_client.post(
    "/pay",
    json={"amount": 100, "order_id": order_id},
    max_retries=1,  # 支付请求重试需谨慎
)
```

### 2. 📊 数据分析平台

数据分析平台需要可靠地调用外部 API 获取数据：
- **异步支持**：同时调用多个数据源，提高数据获取效率
- **自动重试**：处理数据源的临时不可用
- **结构化日志**：监控数据获取状态，便于排查问题

```python
import asyncio
from relihttp import AsyncClient

async def fetch_data_from_multiple_sources():
    async with AsyncClient(
        timeout=5.0,  # 数据获取可能需要更长时间
        max_retries=3,  # 数据获取可以容忍更多重试
    ) as client:
        # 并行获取多个数据源
        tasks = [
            client.get("https://source1.example.com/data"),
            client.get("https://source2.example.com/data"),
            client.get("https://source3.example.com/data"),
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理响应
        results = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                print(f"Source {i+1} failed: {resp}")
            else:
                results.append(resp.json())
        return results
```

### 3. 📱 移动应用后端

移动应用后端需要处理大量用户请求：
- **限流保护**：防止恶意请求或突发流量
- **熔断机制**：当依赖服务异常时，保护核心功能
- **结构化日志**：监控 API 性能和错误率

```python
# 移动 API 客户端配置
api_client = Client(
    base_url="https://api.example.com",
    timeout=3.0,
    retry="safe",
    max_retries=3,
    rate_limit=500,  # 允许更高的请求速率
    circuit_breaker=True,
    failure_threshold=10,  # 更高的故障阈值
    recovery_timeout=60,  # 更长的恢复时间
)
```

---

## 核心特性

relihttp 具备以下核心功能，让 HTTP 请求变得安全、可靠且易于管理：

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      ⏱️ **智能超时控制**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>✅ 全局默认超时设置</li>
      <li>⚡ 支持单次请求超时覆盖</li>
      <li>📊 精确的超时统计</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      🔄 **安全重试机制**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>📈 指数退避 + 抖动算法</li>
      <li>🌐 仅对安全方法默认重试</li>
      <li>🎯 可配置的重试条件（状态码 + 异常）</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      🚦 **灵活限流策略**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>🔄 令牌桶算法实现</li>
      <li>⚙️ 支持 sleep/raise 两种模式</li>
      <li>📊 平滑的请求速率控制</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      🛡️ **智能熔断保护**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>🚧 三级状态管理：closed/open/half-open</li>
      <li>⚡ 自动恢复机制</li>
      <li>📉 防止级联故障</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      ⚡ **异步客户端支持**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>🔄 完整的 asyncio 支持</li>
      <li>📦 基于 aiohttp 实现</li>
      <li>🎯 与同步客户端 API 一致</li>
      <li>⏱️ 异步版本的所有可靠性特性</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      📝 **结构化日志**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>📊 标准 logging 模块集成</li>
      <li>🔍 丰富的请求上下文信息</li>
      <li>📈 请求/响应/错误事件追踪</li>
    </ul>
  </div>

  <div style="background-color: #f8fafc; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
    <h3 style="display: flex; align-items: center; gap: 10px; margin-top: 0;">
      🏗️ **策略式架构**
    </h3>
    <ul style="list-style-type: disc; padding-left: 20px;">
      <li>🔧 可插拔的策略组件</li>
      <li>⚡ 灵活的自定义扩展</li>
      <li>🎨 松耦合的设计理念</li>
    </ul>
  </div>

</div>

---

## 技术架构

relihttp 采用清晰的分层架构，基于策略模式设计，实现了功能的模块化和可扩展性：

```
┌─────────────────────────────────────────────────────────────┐
│                        Client 层                            │
│  (client.py) - 主客户端类，提供与 requests 兼容的 API        │
│  负责请求的发起和响应的处理                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Policy 层                              │
│  (policies/) - 各种可靠性策略的实现                         │
│  - retry.py      # 重试策略                                │
│  - timeout.py    # 超时策略                                │
│  - rate_limit.py # 限流策略                                │
│  - logger.py     # 日志策略                                │
│  - circuit.py    # 熔断策略                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Transport 层                           │
│  (transport/) - HTTP 传输实现                              │
│  - base.py      # 传输基类                                 │
│  - requests.py  # 基于 requests 的实现                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Core 层                                │
│  (models.py/utils.py) - 核心数据模型和工具函数             │
│  提供上下文管理、工具函数等基础功能                         │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈详情

| 组件类型 | 技术框架 | 版本要求 | 用途说明 |
|---------|---------|---------|---------|
| **核心依赖** | requests | >= 2.28 | HTTP 传输实现（同步） |
| **异步依赖** | aiohttp | >= 3.8 | HTTP 传输实现（异步） |
| **Python 版本** | Python | >= 3.9 | 运行环境 |
| **日志系统** | logging | 标准库 | 结构化日志 |
| **数据验证** | typing_extensions | >= 4.6 | 类型注解支持 |
| **构建工具** | hatchling | >= 1.21 | 项目构建 |

---

## 核心设计：策略模式

relihttp 的核心设计理念是**策略模式**，将各种可靠性特性抽象为可配置、可插拔的策略。这种设计带来了极大的灵活性：

### 策略的工作原理

每个策略可以实现三个核心方法：

1. **before_request**：请求发送前执行（如：超时设置、重试准备）
2. **after_response**：响应返回后执行（如：重试判断、日志记录）
3. **on_error**：请求失败时执行（如：异常处理、熔断判断）

### 内置策略

- **RetryPolicy**：智能重试机制，支持配置重试条件和退避策略
- **TimeoutPolicy**：全局和单次请求超时控制
- **RateLimitPolicy**：令牌桶限流，支持两种工作模式
- **LoggingPolicy**：结构化日志记录，包含请求上下文
- **CircuitBreakerPolicy**：熔断保护，防止级联故障

### 策略组合示例

```python
from relihttp import Client
from relihttp.policies import (
    RetryPolicy,
    TimeoutPolicy,
    RateLimitPolicy,
    LoggingPolicy,
    CircuitBreakerPolicy
)

client = Client(
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3, retry_on_status=[500, 502, 503, 504, 429]),
        RateLimitPolicy(rate_limit=100, mode="sleep"),
        CircuitBreakerPolicy(failure_threshold=5, recovery_timeout=30),
        LoggingPolicy(),
    ]
)
```

---

## 快速开始

### 📋 环境要求
- 🐍 Python 3.9+
- 📦 UV (推荐) 或 pip
- 📚 aiohttp (可选，用于异步客户端)

### 🛠️ 安装部署

1. **安装 UV (推荐)** 📥
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **安装 relihttp** 📦
   ```bash
   # 基本安装（仅同步客户端）
   uv install relihttp
   # 或使用 pip
   pip install relihttp

   # 安装包含异步支持
   uv install relihttp[async]
   # 或使用 pip
   pip install relihttp[async]
   ```

### 🚀 基本使用

#### 同步客户端

```python
from relihttp import Client

# 创建客户端（默认包含基本可靠性特性）
client = Client(
    base_url="https://api.example.com",
    timeout=3.0,
    retry="safe",
    max_retries=3,
    rate_limit=100,
)

# 发送请求（与 requests API 兼容）
resp = client.get("/users")
print(resp.json())

# 单次请求覆盖配置
resp = client.post(
    "/pay",
    json={"amount": 100},
    timeout=1.5,  # 覆盖超时
    max_retries=1,  # 覆盖重试次数
)
```

#### 异步客户端

```python
import asyncio
from relihttp import AsyncClient

async def main():
    # 创建异步客户端
    async with AsyncClient(
        base_url="https://api.example.com",
        timeout=3.0,
        retry="safe",
        max_retries=3,
    ) as client:
        # 发送异步请求
        resp = await client.get("/users")
        print(await resp.json())

        # 单次请求覆盖配置
        resp = await client.post(
            "/pay",
            json={"amount": 100},
            timeout=1.5,
            max_retries=1,
        )

# 运行异步代码
asyncio.run(main())
```

---

## 关键特性详解

### 1. ⏱️ 超时控制

relihttp 提供了灵活的超时设置：

```python
# 全局超时设置
client = Client(timeout=5.0)

# 单次请求覆盖
client.get("/slow-endpoint", timeout=10.0)
```

### 2. 🔄 智能重试

默认仅对安全方法（GET、HEAD、OPTIONS、PUT、DELETE）重试，可配置重试条件：

```python
client = Client(
    retry="safe",  # "safe" 或 "all"
    max_retries=3,
    retry_on_status=[500, 502, 503, 504, 429],
)
```

### 3. 🚦 限流保护

支持两种限流模式：

- **sleep**：等待可用令牌（默认）
- **raise**：快速失败，抛出 RateLimitedError

```python
# 每秒最多 100 个请求，等待可用令牌
client = Client(rate_limit=100, rate_limit_mode="sleep")

# 每秒最多 50 个请求，超过则抛出异常
client = Client(rate_limit=50, rate_limit_mode="raise")
```

### 4. 🛡️ 熔断保护

防止级联故障的熔断机制：

```python
client = Client(
    circuit_breaker=True,
    failure_threshold=5,  # 5次失败后熔断
    recovery_timeout=30,   # 30秒后尝试恢复
    half_open_successes=2, # 需要2次成功才能完全恢复
)
```

### 5. 📝 结构化日志

内置结构化日志，包含丰富的上下文信息：

```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

client = Client()
client.get("https://api.example.com/users")
```

**日志输出示例**：
```
2026-02-03 14:30:00 - relihttp - INFO - event=http.request request_id=abc123 method=GET url=https://api.example.com/users
2026-02-03 14:30:00 - relihttp - INFO - event=http.response request_id=abc123 status_code=200 elapsed_ms=150
```

---

## 📊 性能基准测试

为了评估 relihttp 的性能表现，我们进行了一系列基准测试，对比了 relihttp 与原生 requests 在不同场景下的性能差异。

### 测试环境
- **硬件**：Intel i7-11th Gen, 16GB RAM
- **网络**：本地 HTTP 服务（减少网络波动影响）
- **Python 版本**：3.9.13
- **测试工具**：`httpx-benchmark` 和自定义脚本

### 测试结果

#### 1. 基础性能对比

| 客户端 | 平均延迟 (ms) | QPS | 95% 延迟 (ms) | 99% 延迟 (ms) |
|-------|--------------|-----|--------------|--------------|
| requests | 4.2 | 238 | 8.1 | 12.3 |
| relihttp (默认配置) | 4.5 | 222 | 9.2 | 15.6 |
| relihttp (仅超时控制) | 4.3 | 233 | 8.5 | 13.2 |

#### 2. 不同并发下的性能

```
并发数 | requests QPS | relihttp QPS | 性能差异
-------|--------------|--------------|----------
10     | 245          | 230          | -6.1%
50     | 238          | 225          | -5.5%
100    | 232          | 220          | -5.2%
200    | 225          | 215          | -4.4%
```

#### 3. 重试场景性能

当面对部分失败的场景时，relihttp 的智能重试机制展现出了明显的优势：

| 场景 | 客户端 | 成功请求数 | 总耗时 (s) | 成功率 |
|-----|-------|----------|-----------|--------|
| 10% 失败率 | requests (无重试) | 900 | 3.8 | 90% |
| 10% 失败率 | relihttp (默认重试) | 1000 | 4.2 | 100% |
| 25% 失败率 | requests (无重试) | 750 | 3.2 | 75% |
| 25% 失败率 | relihttp (默认重试) | 985 | 5.1 | 98.5% |

### 性能分析

1. **可靠性开销**：relihttp 的默认配置仅比 requests 慢约 5-6%，但提供了完整的可靠性保证
2. **并发扩展性**：随着并发数增加，性能差异逐渐缩小，显示出良好的扩展性
3. **重试价值**：在不稳定的网络环境下，relihttp 能显著提高请求成功率，虽然增加了总耗时，但确保了业务可靠性

### 优化建议

- **精简策略**：根据业务需求只启用必要的策略
- **合理配置重试**：避免过多的重试次数
- **使用异步客户端**：对于高并发场景，使用 `AsyncClient` 可获得更好的性能

```python
# 性能优化配置示例
client = Client(
    policies=[
        TimeoutPolicy(timeout=2.0),  # 仅保留必要的超时控制
        RetryPolicy(max_retries=2),   # 最小化重试次数
    ]
)
```

---

## 性能优化与最佳实践

relihttp 不仅提供了可靠的默认配置，还支持多种优化策略，让你在保持可靠性的同时获得最佳性能：

### 🎯 策略精简原则

只启用你真正需要的策略，减少不必要的性能开销：

```python
# 针对高性能需求的精简配置
client = Client(
    policies=[
        TimeoutPolicy(timeout=2.0),  # 仅保留必要的超时控制
        RetryPolicy(max_retries=2),   # 最小化重试次数
    ]
)
```

### ⚡ 合理配置重试策略

过多的重试会影响性能，根据业务场景调整重试参数：

```python
# 关键业务的平衡配置
client = Client(
    max_retries=3,           # 3次尝试（含首次）
    retry_delay=0.5,         # 初始延迟0.5秒
    retry_backoff_factor=2,  # 指数退避
)
```

### 📊 连接池与资源管理

relihttp 基于 `requests.Session` 自动复用连接，无需额外配置即可获得连接池的性能优势：

```python
# 连接池默认启用，自动管理TCP连接
client = Client()
```

---

## 开发者工具

为了提升开发体验，relihttp 提供了便捷的命令行工具：

### 🧪 快速测试

```bash
# 测试基本功能
python -m relihttp test get https://httpbin.org/get --timeout 2 --max-retries 2

# 测试复杂请求
python -m relihttp test post https://httpbin.org/post --json '{"key": "value"}'
```

### 📈 性能基准测试

```bash
# 测试不同并发下的性能
python -m relihttp bench https://httpbin.org/get --concurrency 10 --requests 100
```

---

## 优雅的架构设计

relihttp 采用模块化的架构设计，保证了代码的可维护性和可扩展性：

<div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0;">
  <div style="flex: 1; min-width: 250px; background: #f8fafc; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">🎯 核心层</h4>
    <p style="font-size: 0.9rem; color: #4b5563;">Client 类和核心数据模型，提供与 requests 兼容的 API</p>
  </div>
  
  <div style="flex: 1; min-width: 250px; background: #f8fafc; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">🛡️ 策略层</h4>
    <p style="font-size: 0.9rem; color: #4b5563;">各种可靠性策略的实现，如重试、超时、限流和熔断</p>
  </div>
  
  <div style="flex: 1; min-width: 250px; background: #f8fafc; padding: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">🚀 传输层</h4>
    <p style="font-size: 0.9rem; color: #4b5563;">HTTP 传输实现，默认基于 requests，支持自定义扩展</p>
  </div>
</div>

---

## 为什么选择 relihttp？

<div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0;">

  <div style="flex: 1; min-width: 260px; background: #f8fafc; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">🎯 默认可靠</h4>
    <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.6;">
      内置超时、重试、限流与熔断机制，无需额外配置即可获得生产级可靠性，
      让“可靠”成为默认行为而非额外负担。
    </p>
  </div>

  <div style="flex: 1; min-width: 260px; background: #f8fafc; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">⚡ 低学习成本</h4>
    <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.6;">
      与 requests API 高度兼容，已有经验的开发者几乎可以零学习成本迁移，
      在熟悉的使用方式中获得更强大的能力。
    </p>
  </div>

  <div style="flex: 1; min-width: 260px; background: #f8fafc; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">🔧 高度可扩展</h4>
    <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.6;">
      策略式架构支持自由组合与替换策略模块，
      能根据不同业务场景定制专属的可靠性方案。
    </p>
  </div>

  <div style="flex: 1; min-width: 260px; background: #f8fafc; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">📊 可观测性</h4>
    <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.6;">
      内置结构化日志与请求上下文追踪，
      可轻松接入 ELK、Loki 或 APM 系统，提升问题定位效率。
    </p>
  </div>

  <div style="flex: 1; min-width: 260px; background: #f8fafc; padding: 18px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
    <h4 style="margin-top: 0; color: #2563eb;">⚡ 异步一致体验</h4>
    <p style="font-size: 0.92rem; color: #4b5563; line-height: 1.6;">
      提供与同步 API 风格一致的 AsyncClient，
      在 asyncio 场景下也能获得同样的可靠性与开发体验。
    </p>
  </div>

</div>

---

## 未来展望

relihttp 目前处于 Alpha 阶段，未来将持续改进和扩展：

### 近期计划 📅
- **更丰富的监控指标** - 提供更详细的性能和可靠性统计
- **HTTP/2 支持** - 支持现代 HTTP 协议
- **更完善的异步策略** - 扩展异步客户端的功能

### 长期愿景 🌟
- 成为 Python 生态中默认可靠的 HTTP 客户端标准
- 提供完整的企业级可靠性解决方案
- 建立活跃的社区，共同推动项目发展

---

## 加入我们

relihttp 是一个开源项目，欢迎大家参与贡献：

- 🐛 报告 Bug：[GitHub Issues](https://github.com/fzf54122/relihttp/issues)
- 📝 提交代码：[Pull Requests](https://github.com/fzf54122/relihttp/pulls)
- 💡 提出建议：通过 Issue 或讨论区分享你的想法

### 致谢 🙏

特别感谢以下项目和社区的支持：

- **requests** - 优秀的 HTTP 客户端库，为 relihttp 提供了坚实的基础
- **uv** - 现代化的 Python 包管理器，提升了开发体验
- **所有贡献者** - 感谢你们的智慧和努力

---

## 许可证

relihttp 采用 MIT License 开源，允许自由使用、修改和分发。

---

<div align="center">
  <img src="./assets/img/relihttp-icon.svg" alt="relihttp Logo" width="120" height="120" >
</div>