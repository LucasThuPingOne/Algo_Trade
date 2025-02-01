# Algo Trade Project in Python
Write by Lucas Thu Ping One (thupingonelucas@gmail.com)

## 📌 Project Overview
This project aims to develop an automated trading algorithm based on a momentum strategy. The goal is to identify trading opportunities by leveraging market trends and price volatility.

## 💡 General Idea
The algorithm uses technical indicators to detect buy and sell signals. It relies on price movements and Bollinger Bands to anticipate trend reversals or continuation phases. 

## 🛠️ Technologies Used
- **Language**: Python
- **Main Libraries**:
  - `pandas`: Data manipulation and processing
  - `numpy`: Mathematical and statistical computations
  - `matplotlib` & `seaborn`: Data visualization
  - `scipy`: optimization

## 📊 Indicators Used
### 1️⃣ Relative Strength Index (RSI)
- Measures momentum by indicating whether an asset is overbought (>70) or oversold (<30).
- Can be used to confirm trends and avoid false signals.

### 2️⃣ Simple Moving Average (SMA)
- Calculates the average price over a specific period (e.g., 20 days).
- Used to identify trends and support/resistance levels.

### 3️⃣ Stochastic Oscillator (SO)
- Measures the closing price relative to the price range over a specific period.
- Buy Signal: When %K crosses above %D in the oversold region (<20).
- Sell Signal: When %K crosses below %D in the overbought region (>80).

### 4️⃣ Bollinger Bands
- **Simple Moving Average (SMA)**: Used as the middle band.
- **Upper Band**: SMA + (k * Standard Deviation).
- **Lower Band**: SMA - (k * Standard Deviation).
- **Signals**:
  - Buy: When the price touches or falls below the lower band.
  - Sell: When the price touches or exceeds the upper band.

## 📈 Backtesting & Performance
- Backtesting conducted on historical S&P 500 data.
- Performance comparison with a benchmark (e.g., S&P 500 or Buy & Hold).
- Evaluation metrics:
  - P&L
  - Winning vs. Losing Trades

## 🔍 Future Indicator Ideas
### 1️⃣ Exponential Moving Average (EMA)
- Similar to SMA but gives more weight to recent prices, making it more responsive to new trends.
- Used to identify short-term trends more effectively.

### 2️⃣ Moving Average Convergence Divergence (MACD)
- Compares two EMAs (e.g., 12-day and 26-day) to identify momentum changes.
- Signals:
  - Buy: When MACD crosses above the signal line.
  - Sell: When MACD crosses below the signal line.

### 3️⃣ Volume Weighted Average Price (VWAP)
- Measures the average price of an asset weighted by volume.
- Used by institutional traders to assess fair value and market trends.

### 4️⃣ Fibonacci Retracement
- Identifies potential support and resistance levels using Fibonacci ratios (e.g., 23.6%, 38.2%, 50%, 61.8%).
- Helps in determining entry and exit points.

### 5️⃣ Machine Learning for Predictive Analysis
- Training models using historical price data to predict future price movements.
- Possible methods:
  - **Supervised Learning**: Using labeled data to predict price trends.
  - **Unsupervised Learning**: Clustering similar trading patterns.
  - **Reinforcement Learning**: Optimizing trading strategies dynamically.
