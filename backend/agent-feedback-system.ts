/**
 * ========================================================================
   AGENT FEEDBACK & IMPROVEMENT SYSTEM
   ========================================================================
 */

import fs from 'fs';
import path from 'path';

export interface FeedbackData {
  agentId: string;
  inferenceId: string;
  timestamp: string;
  feedback: {
    rating: number; // 1-3 (bad, neutral, good)
    comments: string;
    outcome?: 'success' | 'failure' | 'partial';
    actualResult?: number;
    expectedResult?: number;
  };
  context: {
    marketConditions: string;
    symbol: string;
    timeframe: string;
    confidence?: number;
    latency?: number;
  };
}

interface PerformanceMetrics {
  accuracy: number;
  confidence: number;
  profitLoss: number;
  decisionCount: number;
  averageLatency: number;
  successRate: number;
}

/**
 * Système de feedback pour améliorer les performances des agents
 */
export class AgentFeedbackSystem {
  private feedbackDir: string;
  private performanceDir: string;

  constructor() {
    this.feedbackDir = path.join(process.cwd(), 'logs', 'feedback');
    this.performanceDir = path.join(process.cwd(), 'logs', 'performance');

    this.ensureDirectories();
  }

  private ensureDirectories() {
    [this.feedbackDir, this.performanceDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  /**
   * Enregistrer le feedback utilisateur sur une inférence
   */
  async recordFeedback(feedback: FeedbackData): Promise<boolean> {
    try {
      const feedbackFile = path.join(this.feedbackDir, `${feedback.agentId}_feedback.json`);
      const existingFeedback = this.loadFeedback(feedback.agentId);

      // Ajouter le nouveau feedback
      existingFeedback.push(feedback);

      // Garder seulement les 1000 derniers feedbacks par agent
      if (existingFeedback.length > 1000) {
        existingFeedback.splice(0, existingFeedback.length - 1000);
      }

      // Sauvegarder
      fs.writeFileSync(feedbackFile, JSON.stringify({
        agentId: feedback.agentId,
        feedbacks: existingFeedback,
        lastUpdated: new Date().toISOString()
      }, null, 2));

      // Mettre à jour les métriques de performance
      await this.updatePerformanceMetrics(feedback.agentId);

      // Générer des suggestions d'amélioration
      await this.generateImprovementSuggestions(feedback.agentId);

      console.log(`[FEEDBACK] Feedback recorded for agent ${feedback.agentId}`);
      return true;

    } catch (error) {
      console.error(`[FEEDBACK] Error recording feedback:`, error);
      return false;
    }
  }

  /**
   * Analyser les patterns de feedback pour identifier les faiblesses
   */
  async analyzeFeedbackPatterns(agentId: string): Promise<any> {
    const feedbacks = this.loadFeedback(agentId);

    if (feedbacks.length < 10) {
      return { message: 'Not enough data for analysis' };
    }

    const analysis = {
      decisionAccuracy: this.calculateDecisionAccuracy(feedbacks),
      confidenceVsReality: this.analyzeConfidenceVsReality(feedbacks),
      marketConditionPerformance: this.analyzeMarketConditionPerformance(feedbacks),
      commonFailurePatterns: this.identifyFailurePatterns(feedbacks),
      improvementOpportunities: this.identifyImprovementOpportunities(feedbacks)
    };

    return analysis;
  }

  /**
   * Calculer le taux de précision des décisions
   */
  private calculateDecisionAccuracy(feedbacks: FeedbackData[]): number {
    const outcomeFeedbacks = feedbacks.filter(f => f.feedback.outcome);
    if (outcomeFeedbacks.length === 0) return 0;

    const successful = outcomeFeedbacks.filter(f => f.feedback.outcome === 'success').length;
    return (successful / outcomeFeedbacks.length) * 100;
  }

  /**
   * Analyser la corrélation entre confiance et réalité
   */
  private analyzeConfidenceVsReality(feedbacks: FeedbackData[]): any {
    const confidenceReality = feedbacks
      .filter(f => f.feedback.outcome && f.context.confidence)
      .map(f => ({
        confidence: f.context.confidence,
        success: f.feedback.outcome === 'success'
      }));

    if (confidenceReality.length === 0) return null;

    // Calculer la corrélation
    const avgConfidenceSuccess = confidenceReality
      .filter(c => c.success)
      .reduce((sum, c) => sum + c.confidence, 0) /
      confidenceReality.filter(c => c.success).length;

    const avgConfidenceFailure = confidenceReality
      .filter(c => !c.success)
      .reduce((sum, c) => sum + c.confidence, 0) /
      confidenceReality.filter(c => !c.success).length;

    return {
      avgConfidenceSuccess,
      avgConfidenceFailure,
      correlation: avgConfidenceSuccess > avgConfidenceFailure ? 'positive' : 'negative'
    };
  }

  /**
   * Analyser la performance par condition de marché
   */
  private analyzeMarketConditionPerformance(feedbacks: FeedbackData[]): any {
    const performanceByCondition = {};

    feedbacks.forEach(feedback => {
      const condition = feedback.context.marketConditions || 'unknown';
      if (!performanceByCondition[condition]) {
        performanceByCondition[condition] = { success: 0, total: 0 };
      }
      performanceByCondition[condition].total++;
      if (feedback.feedback.outcome === 'success') {
        performanceByCondition[condition].success++;
      }
    });

    // Calculer les taux de succès
    Object.keys(performanceByCondition).forEach(condition => {
      const data = performanceByCondition[condition];
      data.successRate = (data.success / data.total) * 100;
    });

    return performanceByCondition;
  }

  /**
   * Identifier les patterns d'échec communs
   */
  private identifyFailurePatterns(feedbacks: FeedbackData[]): any {
    const failures = feedbacks.filter(f => f.feedback.outcome === 'failure');

    return {
      lowConfidenceFailures: failures.filter(f => (f.context.confidence || 0) < 60).length,
      highVolatilityFailures: failures.filter(f =>
        f.context.marketConditions?.includes('high_volatility')
      ).length,
      specificSymbolFailures: this.analyzeSymbolFailures(failures),
      timeBasedFailures: this.analyzeTimeBasedFailures(failures)
    };
  }

  /**
   * Analyser les échecs spécifiques aux symboles
   */
  private analyzeSymbolFailures(failures: FeedbackData[]): any {
    const symbolFailures: { [symbol: string]: number } = {};

    failures.forEach(failure => {
      const symbol = failure.context.symbol || 'unknown';
      symbolFailures[symbol] = (symbolFailures[symbol] || 0) + 1;
    });

    return Object.entries(symbolFailures)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([symbol, count]) => ({ symbol, count }));
  }

  /**
   * Analyser les échecs basés sur le temps
   */
  private analyzeTimeBasedFailures(failures: FeedbackData[]): any {
    const hours = new Array(24).fill(0);

    failures.forEach(failure => {
      const hour = new Date(failure.timestamp).getHours();
      hours[hour]++;
    });

    return {
      worstHour: hours.indexOf(Math.max(...hours)),
      hourDistribution: hours
    };
  }

  /**
   * Identifier les opportunités d'amélioration
   */
  private identifyImprovementOpportunities(feedbacks: FeedbackData[]): any[] {
    const opportunities = [];

    // Analyse de la confiance
    const confidenceAnalysis = this.analyzeConfidenceVsReality(feedbacks);
    if (confidenceAnalysis && confidenceAnalysis.correlation === 'negative') {
      opportunities.push({
        type: 'confidence_calibration',
        priority: 'high',
        description: 'La confiance de l\'agent est mal calibrée',
        suggestion: 'Réduire le seuil de confiance ou améliorer les métriques de confiance',
        expectedImprovement: '+15% précision'
      });
    }

    // Analyse des conditions de marché
    const marketPerformance = this.analyzeMarketConditionPerformance(feedbacks);
    Object.entries(marketPerformance).forEach(([condition, data]: [string, any]) => {
      if (data.successRate < 50 && data.total > 5) {
        opportunities.push({
          type: 'market_condition_optimization',
          priority: 'medium',
          description: `Performance faible en conditions: ${condition}`,
          suggestion: `Entraîner l\'agent spécifiquement pour ${condition}`,
          expectedImprovement: `+${(100 - data.successRate).toFixed(0)}% précision pour ${condition}`
        });
      }
    });

    return opportunities;
  }

  /**
   * Générer des suggestions d'amélioration automatiques
   */
  async generateImprovementSuggestions(agentId: string): Promise<any> {
    const patterns = await this.analyzeFeedbackPatterns(agentId);
    const suggestionsFile = path.join(this.feedbackDir, `${agentId}_suggestions.json`);

    const suggestions = {
      agentId,
      generatedAt: new Date().toISOString(),
      patterns,
      suggestions: patterns.improvementOpportunities || [],
      implementationPlan: this.generateImplementationPlan(patterns.improvementOpportunities || [])
    };

    fs.writeFileSync(suggestionsFile, JSON.stringify(suggestions, null, 2));
    return suggestions;
  }

  /**
   * Générer un plan d'implémentation
   */
  private generateImplementationPlan(opportunities: any[]): any {
    const plan = {
      immediate: [], // Actions à faire immédiatement
      shortTerm: [],  // Actions à court terme (1-2 semaines)
      longTerm: []    // Actions à long terme (1 mois+)
    };

    opportunities.forEach(opp => {
      const action = {
        title: opp.description,
        steps: this.getImplementationSteps(opp.type),
        estimatedTime: this.getEstimatedTime(opp.type),
        resources: this.getRequiredResources(opp.type)
      };

      if (opp.priority === 'high') {
        plan.immediate.push(action);
      } else if (opp.priority === 'medium') {
        plan.shortTerm.push(action);
      } else {
        plan.longTerm.push(action);
      }
    });

    return plan;
  }

  /**
   * Obtenir les étapes d'implémentation
   */
  private getImplementationSteps(type: string): string[] {
    const steps = {
      confidence_calibration: [
        'Analyser les métriques de confiance actuelles',
        'Identifier les biais de calibration',
        'Ajuster l\'algorithme de calcul de confiance',
        'Tester avec les données historiques',
        'Déployer et monitorer'
      ],
      market_condition_optimization: [
        'Collecter plus de données pour cette condition',
        'Créer un modèle spécialisé pour la condition',
        'Entraîner sur les données historiques pertinentes',
        'Valider avec backtesting',
        'Intégrer dans l\'agent principal'
      ]
    };

    return steps[type] || ['Analyser le problème', 'Développer une solution', 'Tester et déployer'];
  }

  /**
   * Obtenir le temps estimé d'implémentation
   */
  private getEstimatedTime(type: string): string {
    const times = {
      confidence_calibration: '2-3 jours',
      market_condition_optimization: '1-2 semaines'
    };

    return times[type] || '1 semaine';
  }

  /**
   * Obtenir les ressources requises
   */
  private getRequiredResources(type: string): string[] {
    const resources = {
      confidence_calibration: ['Data scientist', 'Données historiques', 'Environment de test'],
      market_condition_optimization: ['Data scientist', 'Infrastructure GPU', 'Plus de données de marché']
    };

    return resources[type] || ['Developpeur', 'Environment de test'];
  }

  /**
   * Mettre à jour les métriques de performance
   */
  private async updatePerformanceMetrics(agentId: string): Promise<void> {
    const feedbacks = this.loadFeedback(agentId);
    const performanceFile = path.join(this.performanceDir, `${agentId}_metrics.json`);

    const metrics: PerformanceMetrics = {
      accuracy: this.calculateDecisionAccuracy(feedbacks),
      confidence: this.calculateAverageConfidence(feedbacks),
      profitLoss: this.calculateProfitLoss(feedbacks),
      decisionCount: feedbacks.length,
      averageLatency: this.calculateAverageLatency(feedbacks),
      successRate: this.calculateSuccessRate(feedbacks)
    };

    fs.writeFileSync(performanceFile, JSON.stringify({
      agentId,
      metrics,
      lastUpdated: new Date().toISOString()
    }, null, 2));
  }

  /**
   * Calculer la confiance moyenne
   */
  private calculateAverageConfidence(feedbacks: FeedbackData[]): number {
    const confidenceValues = feedbacks
      .map(f => f.context.confidence || 0)
      .filter(c => c > 0);

    return confidenceValues.length > 0
      ? confidenceValues.reduce((sum, c) => sum + c, 0) / confidenceValues.length
      : 0;
  }

  /**
   * Calculer le profit/loss
   */
  private calculateProfitLoss(feedbacks: FeedbackData[]): number {
    return feedbacks
      .filter(f => f.feedback.actualResult && f.feedback.expectedResult)
      .reduce((sum, f) => sum + (f.feedback.actualResult! - f.feedback.expectedResult!), 0);
  }

  /**
   * Calculer la latence moyenne
   */
  private calculateAverageLatency(feedbacks: FeedbackData[]): number {
    const latencies = feedbacks
      .map(f => f.context.latency || 0)
      .filter(l => l > 0);

    return latencies.length > 0
      ? latencies.reduce((sum, l) => sum + l, 0) / latencies.length
      : 0;
  }

  /**
   * Calculer le taux de succès
   */
  private calculateSuccessRate(feedbacks: FeedbackData[]): number {
    const withOutcome = feedbacks.filter(f => f.feedback.outcome);
    if (withOutcome.length === 0) return 0;

    const successful = withOutcome.filter(f => f.feedback.outcome === 'success').length;
    return (successful / withOutcome.length) * 100;
  }

  /**
   * Charger les feedbacks existants
   */
  private loadFeedback(agentId: string): FeedbackData[] {
    const feedbackFile = path.join(this.feedbackDir, `${agentId}_feedback.json`);

    try {
      if (fs.existsSync(feedbackFile)) {
        const data = JSON.parse(fs.readFileSync(feedbackFile, 'utf8'));
        return data.feedbacks || [];
      }
    } catch (error) {
      console.error(`Error loading feedback for ${agentId}:`, error);
    }

    return [];
  }

  /**
   * Obtenir les métriques de performance actuelles
   */
  getPerformanceMetrics(agentId: string): PerformanceMetrics | null {
    const performanceFile = path.join(this.performanceDir, `${agentId}_metrics.json`);

    try {
      if (fs.existsSync(performanceFile)) {
        const data = JSON.parse(fs.readFileSync(performanceFile, 'utf8'));
        return data.metrics;
      }
    } catch (error) {
      console.error(`Error loading metrics for ${agentId}:`, error);
    }

    return null;
  }
}

// Export singleton instance
export const agentFeedbackSystem = new AgentFeedbackSystem();
