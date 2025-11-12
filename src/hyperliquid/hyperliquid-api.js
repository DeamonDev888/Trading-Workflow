/**
 * HyperLiquid API Client - JavaScript Clean Version
 * Tous les appels API réels pour le trading sur HyperLiquid
 */

const axios = require('axios');

class HyperliquidAPI {
  constructor(privateKey = null, useTestnet = false) {
    this.baseUrl = useTestnet
      ? 'https://api.hyperliquid-testnet.xyz'
      : 'https://api.hyperliquid.xyz';
    this.wsUrl = useTestnet
      ? 'wss://api.hyperliquid-testnet.xyz/ws'
      : 'wss://api.hyperliquid.xyz/ws';
    this.privateKey = privateKey;
    this.address = null;

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000, // 30 secondes timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.assetMapping = {
      BTC: 0, ETH: 1, SOL: 2, ARB: 3, OP: 4, MNT: 5, BLUR: 6, SUI: 7,
      APT: 8, DYDX: 9, LDO: 10, INJ: 11, AAVE: 12, LINK: 13, UNI: 14,
      FXS: 15, GALA: 16, APE: 17, SAND: 18, MANA: 19, STG: 20, RDNT: 21,
      CFX: 22, IMX: 23, FTM: 24, PEPE: 25, AR: 26, MAGIC: 27, MKR: 28,
      SNX: 29, CRV: 30, COMP: 31, YFI: 32, SUSHI: 33, '1INCH': 34, BAT: 35,
      ZRX: 36, KNC: 38, MANTA: 39, BONK: 40, WIF: 41, BOME: 42, FLOKI: 43,
      POPCAT: 44, MEW: 45, NEIRO: 46, ACT: 47, PNUT: 48,
    };
  }

  async getAllMids() {
    try {
      const response = await this.client.post('/info', {
        type: 'allMids',
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getAllMids:', error);
      throw error;
    }
  }

  async getAllTokens() {
    try {
      const response = await this.client.post('/info', {
        type: 'allMids',
      });
      // Retourne les mids sous forme de liste de tokens
      const mids = response.data;
      if (Array.isArray(mids)) {
        // Format: [symbol1, price1, symbol2, price2, ...]
        const tokens = [];
        for (let i = 0; i < mids.length; i += 2) {
          if (mids[i] && mids[i + 1]) {
            tokens.push({
              symbol: mids[i],
              price: mids[i + 1]
            });
          }
        }
        return tokens;
      } else if (typeof mids === 'object') {
        // Format: {symbol1: price1, symbol2: price2, ...}
        return Object.entries(mids).map(([symbol, price]) => ({
          symbol,
          price
        }));
      }
      return [];
    } catch (error) {
      console.error('Erreur getAllTokens:', error);
      throw error;
    }
  }

  async getTokenPrice(symbol) {
    try {
      const response = await this.client.post('/info', {
        type: 'allMids',
      });
      const mids = response.data;

      if (Array.isArray(mids)) {
        // Format: [symbol1, price1, symbol2, price2, ...]
        for (let i = 0; i < mids.length; i += 2) {
          if (mids[i] === symbol) {
            return mids[i + 1];
          }
        }
      } else if (typeof mids === 'object') {
        // Format: {symbol1: price1, symbol2: price2, ...}
        return mids[symbol];
      }

      throw new Error(`Symbol ${symbol} not found`);
    } catch (error) {
      console.error(`Erreur getTokenPrice pour ${symbol}:`, error);
      throw error;
    }
  }

  async getMeta() {
    try {
      const response = await this.client.post('/info', {
        type: 'meta',
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getMeta:', error);
      throw error;
    }
  }

  async getMetaAndAssetCtxs() {
    try {
      const response = await this.client.post('/info', {
        type: 'metaAndAssetCtxs',
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getMetaAndAssetCtxs:', error);
      throw error;
    }
  }

  async getUserState(address) {
    try {
      const response = await this.client.post('/info', {
        type: 'userState',
        user: address,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getUserState:', error);
      throw error;
    }
  }

  async getOpenOrders(address) {
    try {
      const response = await this.client.post('/info', {
        type: 'openOrders',
        user: address,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getOpenOrders:', error);
      throw error;
    }
  }

  async placeOrder(address, isBuy, symbol, price, size, reduceOnly = false, ioc = false) {
    try {
      const coinIndex = this.assetMapping[symbol];
      if (coinIndex === undefined) {
        throw new Error(`Symbol ${symbol} not supported`);
      }

      const orderData = {
        a: coinIndex,
        b: isBuy,
        p: price.toString(),
        s: size.toString(),
        r: reduceOnly,
        t: {
          limit: {
            tif: ioc ? 'Ioc' : 'Gtc',
          },
        },
      };

      const response = await this.client.post('/exchange', {
        type: 'order',
        order: orderData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur placeOrder:', error);
      throw error;
    }
  }

  async cancelOrder(address, orderId) {
    try {
      const cancelData = {
        asset: 0,
        isBuy: false,
        id: orderId,
      };

      const response = await this.client.post('/exchange', {
        type: 'cancel',
        cancelByCloid: cancelData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur cancelOrder:', error);
      throw error;
    }
  }

  async cancelAllOrders(address) {
    try {
      const openOrders = await this.getOpenOrders(address);

      if (!openOrders.orders || openOrders.orders.length === 0) {
        return { status: 'No orders to cancel' };
      }

      const cancels = openOrders.orders.map((order) => ({
        asset: order.asset,
        isBuy: order.isBuy,
        id: order.id,
      }));

      const cancelData = {
        asset: 0,
        isBuy: false,
        id: 0,
        cancels: cancels,
      };

      const response = await this.client.post('/exchange', {
        type: 'cancelByCloid',
        cancelByCloid: cancelData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur cancelAllOrders:', error);
      throw error;
    }
  }

  async modifyOrder(address, orderId, price, size) {
    try {
      const modifyData = {
        id: orderId,
        limitPx: price,
        sz: size,
      };

      const response = await this.client.post('/exchange', {
        type: 'modify',
        modify: modifyData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur modifyOrder:', error);
      throw error;
    }
  }

  async setLeverage(address, asset, leverage) {
    try {
      const leverageData = {
        asset: asset,
        isBuy: true,
        leverage: leverage,
      };

      const response = await this.client.post('/exchange', {
        type: 'leverage',
        leverage: leverageData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur setLeverage:', error);
      throw error;
    }
  }

  async transfer(address, destination, asset, amount) {
    try {
      const transferData = {
        destination: destination,
        asset: asset,
        amount: amount,
      };

      const response = await this.client.post('/exchange', {
        type: 'transfer',
        transfer: transferData,
        signature: '',
      });

      return response.data;
    } catch (error) {
      console.error('Erreur transfer:', error);
      throw error;
    }
  }

  async getCandleSnapshot(symbol, interval = '1m') {
    try {
      const response = await this.client.post('/info', {
        type: 'candleSnapshot',
        coin: symbol,
        interval: interval,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getCandleSnapshot:', error);
      throw error;
    }
  }

  async getCandles(symbol, startTime, endTime) {
    try {
      const response = await this.client.post('/info', {
        type: 'candle',
        coin: symbol,
        startTime: startTime,
        endTime: endTime,
        interval: '1m',
      });
      return response.data;
    } catch (error) {
      console.error('Erreur getCandles:', error);
      throw error;
    }
  }

  async getVolumeData(symbols) {
    try {
      const volumes = {};

      for (const symbol of symbols) {
        try {
          const coinIndex = this.assetMapping[symbol];
          if (coinIndex !== undefined) {
            volumes[symbol] = await this.getMetaAndAssetCtxs();
          }
        } catch (error) {
          console.warn(`Erreur volume pour ${symbol}:`, error);
        }
      }

      return volumes;
    } catch (error) {
      console.error('Erreur getVolumeData:', error);
      throw error;
    }
  }

  async getPerformance(address) {
    try {
      const userState = await this.getUserState(address);
      const openOrders = await this.getOpenOrders(address);

      return {
        accountValue: userState.marginSummary?.accountValue || 0,
        totalMarginUsed: userState.marginSummary?.totalMarginUsed || 0,
        openOrders: openOrders.orders?.length || 0,
        positions: userState.assetPositions?.length || 0,
      };
    } catch (error) {
      console.error('Erreur getPerformance:', error);
      throw error;
    }
  }
}

module.exports = HyperliquidAPI;
