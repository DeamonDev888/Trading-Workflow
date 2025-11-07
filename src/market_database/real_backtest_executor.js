/**
 * REAL BACKTEST EXECUTOR
 * Executes backtests on real market data from database
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const MarketDatabase = require('./setup_database');

class RealBacktestExecutor {
  constructor() {
    this.marketDb = new MarketDatabase();
    this.db = null;
    this.initialBalance = 1000000; // 1M USD
  }

  async initialize() {
    await this.marketDb.initialize();
    this.db = this.marketDb.db;
    console.log('✅ Connected to market database for backtesting');
  }

  /**
   * Execute backtest on real market data
   */
  async executeBacktest(strategy, symbol, timeframe = '1h') {
    try {
      console.log(`🔧 Executing real backtest: ${strategy} on ${symbol}`);

      // Get real OHLCV data
      const ohlcvData = await this.getRealMarketData(symbol, timeframe);

      if (ohlcvData.length < 100) {
        throw new Error(
          `Insufficient data: only ${ohlcvData.length} candles available`
        );
      }

      // Execute strategy
      const results = await this.runStrategy(strategy, ohlcvData);

      // Save results to database
      await this.saveBacktestResults(strategy, symbol, timeframe, results);

      console.log(`✅ Backtest completed for ${strategy}`);
      return results;
    } catch (error) {
      console.error(`❌ Backtest failed for ${strategy}:`, error.message);
      throw error;
    }
  }

  /**
   * Get real market data from database
   */
  async getRealMarketData(symbol, timeframe, limit = 1000) {
    return new Promise((resolve, reject) => {
      const query = `
                SELECT timestamp, open, high, low, close, volume
                FROM ohlcv_data
                WHERE symbol = ? AND timeframe = ?
                ORDER BY timestamp ASC
                LIMIT ?
            `;

      this.db.all(query, [symbol, timeframe, limit], (err, rows) => {
        if (err) {
          reject(err);
          return;
        }
        resolve(rows);
      });
    });
  }

  /**
   * Run trading strategy on real data
   */
  async runStrategy(strategyName, ohlcvData) {
    const results = {
      strategy: strategyName,
      symbol: ohlcvData[0]?.symbol || 'UNKNOWN',
      trades: [],
      balance: this.initialBalance,
      positions: [],
      equityCurve: [this.initialBalance],
      timestamps: [ohlcvData[0]?.timestamp],
      maxBalance: this.initialBalance,
      minBalance: this.initialBalance,
      sharpeRatio: 0,
      maxDrawdown: 0,
      totalReturn: 0,
      winRate: 0,
      profitFactor: 0,
      totalTrades: 0,
    };

    switch (strategyName) {
      case 'GoldenCrossover':
        await this.goldenCrossoverStrategy(ohlcvData, results);
        break;
      case 'RSI_Momentum':
        await this.rsiMomentumStrategy(ohlcvData, results);
        break;
      case 'MACD_Trend':
        await this.macdTrendStrategy(ohlcvData, results);
        break;
      case 'Volume_Breakout':
        await this.volumeBreakoutStrategy(ohlcvData, results);
        break;
      case 'Mean_Reversion':
        await this.meanReversionStrategy(ohlcvData, results);
        break;
      case 'Momentum_Follow':
        await this.momentumFollowStrategy(ohlcvData, results);
        break;
      default:
        throw new Error(`Unknown strategy: ${strategyName}`);
    }

    // Calculate final metrics
    this.calculateFinalMetrics(results);

    return results;
  }

  /**
   * Golden Crossover Strategy (SMA 20/200)
   */
  async goldenCrossoverStrategy(data, results) {
    const sma20 = this.calculateSMA(
      data.map((d) => d.close),
      20
    );
    const sma200 = this.calculateSMA(
      data.map((d) => d.close),
      200
    );

    for (let i = 201; i < data.length; i++) {
      const currentPrice = data[i].close;
      const currentSMA20 = sma20[i - 201];
      const currentSMA200 = sma200[i - 201];

      if (!currentSMA20 || !currentSMA200) continue;

      // Buy signal: SMA20 crosses above SMA200
      if (sma20[i - 202] <= sma200[i - 202] && currentSMA20 > currentSMA200) {
        if (results.positions.length === 0) {
          const positionSize = results.balance * 0.1; // 10% position
          results.positions.push({
            type: 'LONG',
            entryPrice: currentPrice,
            entryTime: data[i].timestamp,
            size: positionSize,
            stopLoss: currentPrice * 0.95, // 5% stop loss
          });
        }
      }

      // Sell signal: SMA20 crosses below SMA200
      if (sma20[i - 202] >= sma200[i - 202] && currentSMA20 < currentSMA200) {
        if (
          results.positions.length > 0 &&
          results.positions[0].type === 'LONG'
        ) {
          const position = results.positions[0];
          const pnl = (currentPrice - position.entryPrice) * position.size;

          results.trades.push({
            type: 'LONG',
            entryPrice: position.entryPrice,
            exitPrice: currentPrice,
            entryTime: position.entryTime,
            exitTime: data[i].timestamp,
            pnl: pnl,
            pnlPercent:
              ((currentPrice - position.entryPrice) / position.entryPrice) *
              100,
          });

          results.balance += pnl;
          results.positions = [];
        }
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);

      // Update max/min balance
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close any remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  /**
   * RSI Momentum Strategy
   */
  async rsiMomentumStrategy(data, results) {
    const rsi = this.calculateRSI(
      data.map((d) => d.close),
      14
    );

    for (let i = 14; i < data.length; i++) {
      const currentPrice = data[i].close;
      const currentRSI = rsi[i - 14];

      if (!currentRSI) continue;

      // Buy signal: RSI oversold (< 30)
      if (currentRSI < 30 && results.positions.length === 0) {
        const positionSize = results.balance * 0.15; // 15% position
        results.positions.push({
          type: 'LONG',
          entryPrice: currentPrice,
          entryTime: data[i].timestamp,
          size: positionSize,
          stopLoss: currentPrice * 0.95,
        });
      }

      // Sell signal: RSI overbought (> 70)
      if (
        currentRSI > 70 &&
        results.positions.length > 0 &&
        results.positions[0].type === 'LONG'
      ) {
        const position = results.positions[0];
        const pnl = (currentPrice - position.entryPrice) * position.size;

        results.trades.push({
          type: 'LONG',
          entryPrice: position.entryPrice,
          exitPrice: currentPrice,
          entryTime: position.entryTime,
          exitTime: data[i].timestamp,
          pnl: pnl,
          pnlPercent:
            ((currentPrice - position.entryPrice) / position.entryPrice) * 100,
        });

        results.balance += pnl;
        results.positions = [];
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  /**
   * MACD Trend Following Strategy
   */
  async macdTrendStrategy(data, results) {
    const macdData = this.calculateMACD(data.map((d) => d.close));

    for (let i = 26; i < data.length; i++) {
      const currentPrice = data[i].close;
      const macdLine = macdData.macd[i - 26];
      const signalLine = macdData.signal[i - 26];

      if (!macdLine || !signalLine) continue;

      // Buy signal: MACD crosses above Signal
      if (
        macdData.macd[i - 27] <= macdData.signal[i - 27] &&
        macdLine > signalLine
      ) {
        if (results.positions.length === 0) {
          const positionSize = results.balance * 0.12; // 12% position
          results.positions.push({
            type: 'LONG',
            entryPrice: currentPrice,
            entryTime: data[i].timestamp,
            size: positionSize,
            stopLoss: currentPrice * 0.94, // 6% stop loss
          });
        }
      }

      // Sell signal: MACD crosses below Signal
      if (
        macdData.macd[i - 27] >= macdData.signal[i - 27] &&
        macdLine < signalLine
      ) {
        if (
          results.positions.length > 0 &&
          results.positions[0].type === 'LONG'
        ) {
          const position = results.positions[0];
          const pnl = (currentPrice - position.entryPrice) * position.size;

          results.trades.push({
            type: 'LONG',
            entryPrice: position.entryPrice,
            exitPrice: currentPrice,
            entryTime: position.entryTime,
            exitTime: data[i].timestamp,
            pnl: pnl,
            pnlPercent:
              ((currentPrice - position.entryPrice) / position.entryPrice) *
              100,
          });

          results.balance += pnl;
          results.positions = [];
        }
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  /**
   * Volume Breakout Strategy
   */
  async volumeBreakoutStrategy(data, results) {
    const volumes = data.map((d) => d.volume);
    const avgVolume = this.calculateSMA(volumes, 20);

    for (let i = 20; i < data.length; i++) {
      const currentPrice = data[i].close;
      const currentVolume = data[i].volume;
      const avgVol = avgVolume[i - 20];

      if (!avgVol) continue;

      // Buy signal: Volume breakout (current > avg * 1.5) and price up
      if (
        currentVolume > avgVol * 1.5 &&
        currentPrice > data[i - 1].close &&
        results.positions.length === 0
      ) {
        const positionSize = results.balance * 0.08; // 8% position
        results.positions.push({
          type: 'LONG',
          entryPrice: currentPrice,
          entryTime: data[i].timestamp,
          size: positionSize,
          stopLoss: currentPrice * 0.96, // 4% stop loss
        });
      }

      // Sell signal: Take profit at 5% or stop loss
      if (
        results.positions.length > 0 &&
        results.positions[0].type === 'LONG'
      ) {
        const position = results.positions[0];
        const pnlPercent =
          ((currentPrice - position.entryPrice) / position.entryPrice) * 100;

        if (pnlPercent >= 5 || pnlPercent <= -4) {
          const pnl = (currentPrice - position.entryPrice) * position.size;

          results.trades.push({
            type: 'LONG',
            entryPrice: position.entryPrice,
            exitPrice: currentPrice,
            entryTime: position.entryTime,
            exitTime: data[i].timestamp,
            pnl: pnl,
            pnlPercent: pnlPercent,
            exitReason: pnlPercent >= 5 ? 'TAKE_PROFIT' : 'STOP_LOSS',
          });

          results.balance += pnl;
          results.positions = [];
        }
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
        exitReason: 'END_OF_DATA',
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  /**
   * Mean Reversion Strategy
   */
  async meanReversionStrategy(data, results) {
    const mean50 = this.calculateSMA(
      data.map((d) => d.close),
      50
    );
    const std20 = this.calculateStandardDeviation(
      data.map((d) => d.close),
      20
    );

    for (let i = 50; i < data.length; i++) {
      const currentPrice = data[i].close;
      const currentMean = mean50[i - 50];
      const currentStd = std20[i - 20];

      if (!currentMean || !currentStd) continue;

      // Buy signal: Price is significantly below mean (2 standard deviations)
      if (
        currentPrice < currentMean - 2 * currentStd &&
        results.positions.length === 0
      ) {
        const positionSize = results.balance * 0.05; // 5% position
        results.positions.push({
          type: 'LONG',
          entryPrice: currentPrice,
          entryTime: data[i].timestamp,
          size: positionSize,
          stopLoss: currentPrice * 0.98,
          targetPrice: currentMean,
        });
      }

      // Sell signal: Return to mean or take profit/stop loss
      if (
        results.positions.length > 0 &&
        results.positions[0].type === 'LONG'
      ) {
        const position = results.positions[0];

        if (
          currentPrice >= position.targetPrice ||
          currentPrice <= position.stopLoss
        ) {
          const pnl = (currentPrice - position.entryPrice) * position.size;

          results.trades.push({
            type: 'LONG',
            entryPrice: position.entryPrice,
            exitPrice: currentPrice,
            entryTime: position.entryTime,
            exitTime: data[i].timestamp,
            pnl: pnl,
            pnlPercent:
              ((currentPrice - position.entryPrice) / position.entryPrice) *
              100,
          });

          results.balance += pnl;
          results.positions = [];
        }
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  /**
   * Momentum Following Strategy
   */
  async momentumFollowStrategy(data, results) {
    const momentum10 = this.calculateMomentum(
      data.map((d) => d.close),
      10
    );

    for (let i = 10; i < data.length; i++) {
      const currentPrice = data[i].close;
      const currentMomentum = momentum10[i - 10];

      if (!currentMomentum) continue;

      // Buy signal: Strong positive momentum (> 2%)
      if (currentMomentum > 2 && results.positions.length === 0) {
        const positionSize = results.balance * 0.1; // 10% position
        results.positions.push({
          type: 'LONG',
          entryPrice: currentPrice,
          entryTime: data[i].timestamp,
          size: positionSize,
          stopLoss: currentPrice * 0.95,
        });
      }

      // Sell signal: Momentum turns negative
      if (
        currentMomentum < 0 &&
        results.positions.length > 0 &&
        results.positions[0].type === 'LONG'
      ) {
        const position = results.positions[0];
        const pnl = (currentPrice - position.entryPrice) * position.size;

        results.trades.push({
          type: 'LONG',
          entryPrice: position.entryPrice,
          exitPrice: currentPrice,
          entryTime: position.entryTime,
          exitTime: data[i].timestamp,
          pnl: pnl,
          pnlPercent:
            ((currentPrice - position.entryPrice) / position.entryPrice) * 100,
        });

        results.balance += pnl;
        results.positions = [];
      }

      // Update equity curve
      if (results.positions.length > 0) {
        const unrealizedPnL =
          (currentPrice - results.positions[0].entryPrice) *
          results.positions[0].size;
        results.equityCurve.push(results.balance + unrealizedPnL);
      } else {
        results.equityCurve.push(results.balance);
      }
      results.timestamps.push(data[i].timestamp);
      results.maxBalance = Math.max(results.maxBalance, results.balance);
      results.minBalance = Math.min(results.minBalance, results.balance);
    }

    // Close remaining positions
    if (results.positions.length > 0) {
      const lastPrice = data[data.length - 1].close;
      const position = results.positions[0];
      const pnl = (lastPrice - position.entryPrice) * position.size;

      results.trades.push({
        type: 'LONG',
        entryPrice: position.entryPrice,
        exitPrice: lastPrice,
        entryTime: position.entryTime,
        exitTime: data[data.length - 1].timestamp,
        pnl: pnl,
        pnlPercent:
          ((lastPrice - position.entryPrice) / position.entryPrice) * 100,
      });

      results.balance += pnl;
      results.positions = [];
      results.equityCurve.push(results.balance);
    }
  }

  // Technical Indicators
  calculateSMA(data, period) {
    const sma = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        sma.push(null);
      } else {
        const sum = data
          .slice(i - period + 1, i + 1)
          .reduce((a, b) => a + b, 0);
        sma.push(sum / period);
      }
    }
    return sma;
  }

  calculateRSI(data, period) {
    const rsi = [];
    const gains = [];
    const losses = [];

    for (let i = 1; i < data.length; i++) {
      const change = data[i] - data[i - 1];
      if (change >= 0) {
        gains.push(change);
        losses.push(0);
      } else {
        gains.push(0);
        losses.push(Math.abs(change));
      }
    }

    for (let i = 0; i < gains.length; i++) {
      if (i < period - 1) {
        rsi.push(null);
      } else {
        const avgGain =
          gains.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) /
          period;
        const avgLoss =
          losses.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0) /
          period;
        const rs = avgGain / avgLoss;
        rsi.push(100 - 100 / (1 + rs));
      }
    }
    return rsi;
  }

  calculateMACD(data) {
    const ema12 = this.calculateEMA(data, 12);
    const ema26 = this.calculateEMA(data, 26);
    const macdLine = [];
    const signalLine = [];

    for (let i = 0; i < ema26.length; i++) {
      if (ema12[i] && ema26[i]) {
        macdLine.push(ema12[i] - ema26[i]);
      } else {
        macdLine.push(null);
      }
    }

    // Signal line is 9-period EMA of MACD line
    for (let i = 0; i < macdLine.length; i++) {
      if (i < 8) {
        signalLine.push(null);
      } else {
        signalLine.push(
          this.calculateEMAValue(macdLine.slice(i - 8, i + 1), 9)
        );
      }
    }

    return { macd: macdLine, signal: signalLine };
  }

  calculateEMA(data, period) {
    const ema = [];
    const multiplier = 2 / (period + 1);
    let previousEMA = data[0]; // Start with first price
    let currentEMA;

    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        ema.push(data[i]);
      } else {
        currentEMA = (data[i] - previousEMA) * multiplier + previousEMA;
        ema.push(currentEMA);
        previousEMA = currentEMA;
      }
    }
    return ema;
  }

  calculateEMAValue(data, period) {
    const multiplier = 2 / (period + 1);
    let ema = data[0];
    for (let i = 1; i < data.length; i++) {
      ema = (data[i] - ema) * multiplier + ema;
    }
    return ema;
  }

  calculateStandardDeviation(data, period) {
    const std = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        std.push(null);
      } else {
        const slice = data.slice(i - period + 1, i + 1);
        const mean = slice.reduce((a, b) => a + b, 0) / period;
        const variance =
          slice.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / period;
        std.push(Math.sqrt(variance));
      }
    }
    return std;
  }

  calculateMomentum(data, period) {
    const momentum = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        momentum.push(null);
      } else {
        momentum.push(((data[i] - data[i - period]) / data[i - period]) * 100);
      }
    }
    return momentum;
  }

  calculateFinalMetrics(results) {
    results.totalTrades = results.trades.length;
    results.totalReturn =
      ((results.balance - this.initialBalance) / this.initialBalance) * 100;

    // Win Rate
    const winningTrades = results.trades.filter((t) => t.pnl > 0);
    results.winRate =
      results.totalTrades > 0
        ? (winningTrades.length / results.totalTrades) * 100
        : 0;

    // Profit Factor
    const totalProfits = winningTrades.reduce((sum, t) => sum + t.pnl, 0);
    const totalLosses = results.trades
      .filter((t) => t.pnl < 0)
      .reduce((sum, t) => sum + Math.abs(t.pnl), 0);
    results.profitFactor = totalLosses > 0 ? totalProfits / totalLosses : 0;

    // Max Drawdown
    let peak = results.initialBalance;
    let maxDD = 0;
    for (const equity of results.equityCurve) {
      if (equity > peak) peak = equity;
      const drawdown = ((peak - equity) / peak) * 100;
      if (drawdown > maxDD) maxDD = drawdown;
    }
    results.maxDrawdown = maxDD;

    // Sharpe Ratio (simplified)
    if (results.equityCurve.length > 1) {
      const returns = [];
      for (let i = 1; i < results.equityCurve.length; i++) {
        returns.push(
          (results.equityCurve[i] - results.equityCurve[i - 1]) /
            results.equityCurve[i - 1]
        );
      }
      const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
      const returnStd = Math.sqrt(
        returns.reduce((acc, r) => acc + Math.pow(r - avgReturn, 2), 0) /
          returns.length
      );
      results.sharpeRatio =
        returnStd > 0 ? (avgReturn / returnStd) * Math.sqrt(252) : 0; // Annualized
    }
  }

  /**
   * Save backtest results to database
   */
  async saveBacktestResults(strategy, symbol, timeframe, results) {
    await this.runQuery(
      `INSERT INTO backtest_results
             (strategy_name, symbol, exchange, timeframe, start_date, end_date,
              total_return, annual_return, sharpe_ratio, max_drawdown,
              total_trades, win_rate, profit_factor, final_balance, initial_balance)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        strategy,
        symbol,
        'binance',
        timeframe,
        results.timestamps[0],
        results.timestamps[results.timestamps.length - 1],
        results.totalReturn,
        (results.totalReturn * 365) /
          (((Date.parse(results.timestamps[results.timestamps.length - 1]) -
            Date.parse(results.timestamps[0])) /
            (1000 * 60 * 60 * 24)) *
            365),
        results.sharpeRatio,
        results.maxDrawdown,
        results.totalTrades,
        results.winRate,
        results.profitFactor,
        results.balance,
        this.initialBalance,
      ]
    );
  }

  async runQuery(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function (err) {
        if (err) {
          reject(err);
          return;
        }
        resolve(this);
      });
    });
  }

  async close() {
    await this.marketDb.close();
  }
}

// Auto-run if this file is executed directly
if (require.main === module) {
  const executor = new RealBacktestExecutor();

  executor
    .initialize()
    .then(() => {
      console.log('🚀 Starting real backtests on market data...');

      // Run multiple strategies on BTC
      const strategies = [
        'GoldenCrossover',
        'RSI_Momentum',
        'MACD_Trend',
        'Volume_Breakout',
        'Mean_Reversion',
        'Momentum_Follow',
      ];
      const promises = [];

      for (const strategy of strategies) {
        promises.push(executor.executeBacktest(strategy, 'BTC/USDT', '1h'));
      }

      return Promise.all(promises);
    })
    .then((results) => {
      console.log('\n📊 BACKTEST RESULTS SUMMARY:');
      console.log('=====================================');

      results.forEach((result, index) => {
        console.log(`\n${index + 1}. ${result.strategy}`);
        console.log(`   Return: ${result.totalReturn.toFixed(2)}%`);
        console.log(`   Sharpe: ${result.sharpeRatio.toFixed(2)}`);
        console.log(`   Win Rate: ${result.winRate.toFixed(2)}%`);
        console.log(`   Max DD: ${result.maxDrawdown.toFixed(2)}%`);
        console.log(`   Trades: ${result.totalTrades}`);
        console.log(
          `   Final Balance: $${(result.balance / 1000000).toFixed(2)}M`
        );
      });

      console.log('\n✅ All real backtests completed successfully!');
    })
    .catch((err) => {
      console.error('❌ Backtest execution failed:', err.message);
    })
    .finally(() => executor.close());
}

module.exports = RealBacktestExecutor;
