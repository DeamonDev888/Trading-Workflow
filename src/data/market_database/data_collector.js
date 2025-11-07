/**
 * REAL MARKET DATA COLLECTOR
 * Collects real OHLCV data from exchanges for backtesting
 */

const axios = require('axios');
const MarketDatabase = require('./setup_database');

class MarketDataCollector {
  constructor() {
    this.db = new MarketDatabase();
    this.exchanges = {
      binance: {
        baseUrl: 'https://api.binance.com/api/v3',
        klines: '/klines',
        serverTime: '/time',
      },
      hyperliquid: {
        // Note: HyperLiquid requires authentication for real-time data
        // We'll start with Binance public data
        baseUrl: 'https://api.hyperliquid.xyz/info',
        spot: '/spot/summary',
        meta: '/meta',
      },
    };
  }

  async initialize() {
    await this.db.initialize();
    await this.db.insertSampleMarkets();
    console.log('🔧 Market data collector initialized');
  }

  /**
   * Collect historical OHLCV data from Binance (public API)
   */
  async collectBinanceOHLCV(symbol, interval = '1h', limit = 1000) {
    try {
      console.log(`📊 Collecting ${symbol} data from Binance...`);

      const response = await axios.get(
        `${this.exchanges.binance.baseUrl}${this.exchanges.binance.klines}`,
        {
          params: {
            symbol: symbol.replace('/', ''),
            interval: interval,
            limit: limit,
          },
          timeout: 10000,
        }
      );

      const klines = response.data;
      const ohlcvData = [];

      for (const kline of klines) {
        const [
          timestamp,
          open,
          high,
          low,
          close,
          volume,
          closeTime,
          quoteAssetVolume,
          numberOfTrades,
          takerBuyBaseAssetVolume,
          takerBuyQuoteAssetVolume,
          ignore,
        ] = kline;

        ohlcvData.push({
          symbol,
          exchange: 'binance',
          timeframe: interval,
          timestamp: new Date(timestamp).toISOString(),
          open: parseFloat(open),
          high: parseFloat(high),
          low: parseFloat(low),
          close: parseFloat(close),
          volume: parseFloat(volume),
        });
      }

      await this.insertOHLCVData(ohlcvData);
      console.log(`✅ Collected ${ohlcvData.length} candles for ${symbol}`);

      return {
        success: true,
        count: ohlcvData.length,
        symbol,
        exchange: 'binance',
        timeframe: interval,
        dateRange: {
          start: ohlcvData[0]?.timestamp,
          end: ohlcvData[ohlcvData.length - 1]?.timestamp,
        },
      };
    } catch (error) {
      console.error(
        `❌ Error collecting ${symbol} from Binance:`,
        error.message
      );
      return {
        success: false,
        error: error.message,
        symbol,
      };
    }
  }

  /**
   * Collect BTC Dominance data from alternative APIs
   */
  async collectBTCDominance() {
    try {
      console.log('📈 Collecting BTC Dominance data...');

      // Using CoinGecko API for BTC Dominance
      const response = await axios.get(
        'https://api.coingecko.com/api/v3/global',
        {
          params: {
            vs_currency: 'usd',
          },
          timeout: 10000,
        }
      );

      const data = response.data.data;

      const btcDominanceData = {
        timestamp: new Date().toISOString(),
        dominance_percentage: data.market_cap_percentage.btc,
        btc_price: null, // Will be filled from BTC price
        total_market_cap: data.total_market_cap.usd,
      };

      // Get current BTC price
      const btcResponse = await axios.get(
        `${this.exchanges.binance.baseUrl}/ticker/price`,
        {
          params: { symbol: 'BTCUSDT' },
        }
      );

      btcDominanceData.btc_price = parseFloat(btcResponse.data.price);

      await this.insertBTCDominanceData(btcDominanceData);

      console.log(
        `✅ BTC Dominance: ${btcDominanceData.dominance_percentage.toFixed(2)}%`
      );

      return {
        success: true,
        dominance: btcDominanceData.dominance_percentage,
        btcPrice: btcDominanceData.btc_price,
        timestamp: btcDominanceData.timestamp,
      };
    } catch (error) {
      console.error('❌ Error collecting BTC Dominance:', error.message);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Insert OHLCV data into database
   */
  async insertOHLCVData(dataArray) {
    for (const data of dataArray) {
      await this.db.runQuery(
        `INSERT OR REPLACE INTO ohlcv_data
                 (symbol, exchange, timeframe, timestamp, open, high, low, close, volume)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          data.symbol,
          data.exchange,
          data.timeframe,
          data.timestamp,
          data.open,
          data.high,
          data.low,
          data.close,
          data.volume,
        ]
      );
    }
  }

  /**
   * Insert BTC Dominance data
   */
  async insertBTCDominanceData(data) {
    await this.db.runQuery(
      `INSERT OR REPLACE INTO btc_dominance
             (timestamp, dominance_percentage, btc_price, total_market_cap)
             VALUES (?, ?, ?, ?)`,
      [
        data.timestamp,
        data.dominance_percentage,
        data.btc_price,
        data.total_market_cap,
      ]
    );
  }

  /**
   * Get data availability statistics
   */
  async getDataStats() {
    const stats = {};

    // Count records per symbol
    const symbolCounts = await this.db.runQuery(`
            SELECT symbol, exchange, COUNT(*) as record_count,
                   MIN(timestamp) as start_date, MAX(timestamp) as end_date
            FROM ohlcv_data
            GROUP BY symbol, exchange
            ORDER BY record_count DESC
        `);

    console.log('📊 Data Availability:');
    console.table(symbolCounts);

    return stats;
  }

  /**
   * Run comprehensive data collection
   */
  async runDataCollection() {
    try {
      console.log('🚀 Starting real market data collection...');

      // Define symbols to collect
      const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'];
      const intervals = ['1h', '4h', '1d'];

      // Collect OHLCV data
      for (const symbol of symbols) {
        for (const interval of intervals) {
          await this.collectBinanceOHLCV(symbol, interval, 500);
          // Small delay to respect API limits
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      }

      // Collect BTC Dominance
      await this.collectBTCDominance();

      // Get statistics
      await this.getDataStats();

      console.log('✅ Data collection completed successfully!');
    } catch (error) {
      console.error('❌ Data collection failed:', error.message);
    }
  }

  async close() {
    await this.db.close();
  }
}

// Auto-run if this file is executed directly
if (require.main === module) {
  const collector = new MarketDataCollector();

  collector
    .initialize()
    .then(() => collector.runDataCollection())
    .catch((err) => console.error('❌ Collection failed:', err.message))
    .finally(() => collector.close());
}

module.exports = MarketDataCollector;
