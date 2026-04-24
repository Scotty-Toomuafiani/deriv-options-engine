# Deriv Synthetic Options Engine
An automated high-frequency trading bot for Volatility 25 Index using WebSockets and AI-driven risk management.

## Phase 1: Infrastructure
- [x] Python Environment Setup (Virtual Environment)
- [x] WebSocket Handshake with Deriv API
- [x] Secure Configuration (.env management)
- [x] Initial Dependency Architecture
# 🚀 Deriv Synthetic Options Engine: Volatility 25 ($R_25$)

A high-frequency algorithmic trading system built in Python, utilizing real-time WebSockets and technical indicators to execute low-latency trades.

## 🛡️ Architectural Decisions
* **Asynchronous Execution:** Built using `asyncio` to handle live WebSocket streams without blocking the event loop.
* **State Management:** Implemented a global `is_in_trade` safety switch to prevent race conditions during high-volatility tick events.
* **Security:** Utilizes `.env` decoupling for industry-standard API secret management.

## 📈 Trading Strategy
* **Indicator:** Relative Strength Index (RSI-14).
* **Trend Filter:** 200-Period Exponential Moving Average (EMA).
* **Logic:** Mean-reversion entries filtered by macro-trend direction to maximize statistical expectancy.

## 🎙️ Interview Prep & Technical FAQ

### Q: Why use a 200 EMA filter for Volatility 25?
**Answer:** To ensure statistical expectancy. In synthetic indices, price can "run" for a long time. The 200 EMA acts as a macro-trend filter, ensuring the bot only attempts mean-reversion (RSI) when it aligns with institutional momentum.

### Q: How did you handle the $0.35 stake risk?
**Answer:** I implemented a "State-Machine" logic. By using a global `is_in_trade` lock and a mandatory 60-second cooldown, I prevented the bot from "revenge trading" or over-leveraging the small account balance during high-volatility spikes.

### Q: Why is the environment structured with .env and venv?
**Answer:** Professionalism and Security. Decoupling the API credentials from the logic prevents accidental exposure of sensitive data, while the virtual environment ensures the system is portable and replicable across different servers.
