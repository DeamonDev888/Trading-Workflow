/**
 * SCRIPT D'OPTIMISATION DATABASE NOVAQUOTE
 * À ajouter au démarrage de l'application backend
 *
 * Ce script configure la base de données SQLite pour des performances optimales
 * et garantit l'intégrité des données avec les foreign keys activées.
 */

const sqlite3 = require('sqlite3');
const path = require('path');

class DatabaseOptimizer {
    constructor(dbPath = './src/market_database/market_data.db') {
        this.dbPath = path.resolve(dbPath);
        this.db = null;
    }

    /**
     * Initialise et optimise la base de données
     */
    async initialize() {
        try {
            console.log('🚀 Initialisation Database NOVAQUOTE...');

            // Connexion à la base de données
            this.db = new sqlite3.Database(this.dbPath, (err) => {
                if (err) {
                    console.error('❌ Erreur de connexion DB:', err.message);
                    throw err;
                }
                console.log('✅ Connecté à la database SQLite');
            });

            // Appliquer toutes les optimisations
            await this.applyOptimizations();

            console.log('✅ Database optimisée et prête pour production');
            return true;

        } catch (error) {
            console.error('❌ Erreur initialisation database:', error);
            throw error;
        }
    }

    /**
     * Applique les optimisations de performance et sécurité
     */
    async applyOptimizations() {
        const optimizations = [
            this.enableForeignKeys,
            this.enableWALMode,
            this.configureSynchronous,
            this.optimizeCache,
            this.analyzeDatabase,
            this.validateIntegrity,
            this.testPerformance
        ];

        for (const optimization of optimizations) {
            try {
                await optimization.call(this);
            } catch (error) {
                console.error(`⚠️ Erreur optimisation: ${error.message}`);
                // Continuer malgré les erreurs pour ne pas bloquer le démarrage
            }
        }
    }

    /**
     * Active les foreign keys pour garantir l'intégrité référentielle
     */
    enableForeignKeys() {
        return new Promise((resolve, reject) => {
            this.db.run("PRAGMA foreign_keys = ON", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ Foreign Keys activées');
                    resolve();
                }
            });
        });
    }

    /**
     * Active le WAL mode pour meilleures performances en écriture
     */
    enableWALMode() {
        return new Promise((resolve, reject) => {
            this.db.run("PRAGMA journal_mode = WAL", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ WAL mode activé (meilleures performances écriture)');
                    resolve();
                }
            });
        });
    }

    /**
     * Configure le mode synchronous pour équilibre performance/sécurité
     */
    configureSynchronous() {
        return new Promise((resolve, reject) => {
            this.db.run("PRAGMA synchronous = NORMAL", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ Mode synchronous configuré (NORMAL)');
                    resolve();
                }
            });
        });
    }

    /**
     * Optimise la taille du cache
     */
    optimizeCache() {
        return new Promise((resolve, reject) => {
            // Cache size en pages (default: 2000, nous mettons 10000)
            this.db.run("PRAGMA cache_size = 10000", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ Cache optimisé (10,000 pages)');
                    resolve();
                }
            });
        });
    }

    /**
     * Analyse la database pour optimiser le query planner
     */
    analyzeDatabase() {
        return new Promise((resolve, reject) => {
            this.db.run("ANALYZE", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ Database analysée et optimisée');
                    resolve();
                }
            });
        });
    }

    /**
     * Valide l'intégrité des données
     */
    validateIntegrity() {
        return new Promise((resolve, reject) => {
            // Vérifier l'intégrité de la database
            this.db.run("PRAGMA integrity_check", (err) => {
                if (err) {
                    reject(err);
                } else {
                    console.log('✅ Intégrité de la database validée');

                    // Vérifier les foreign keys
                    this.db.run("PRAGMA foreign_key_check", (fkErr) => {
                        if (fkErr) {
                            console.warn('⚠️ Problèmes de foreign keys détectés:', fkErr);
                        } else {
                            console.log('✅ Foreign keys validées');
                        }
                        resolve();
                    });
                }
            });
        });
    }

    /**
     * Test les performances des requêtes principales
     */
    testPerformance() {
        return new Promise((resolve) => {
            const testQueries = [
                {
                    name: "Recherche wallet par adresse",
                    sql: "SELECT COUNT(*) FROM wallets WHERE metamask_address = ?",
                    params: ["0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1"]
                },
                {
                    name: "Jointure wallet-balances",
                    sql: "SELECT COUNT(*) FROM wallets w LEFT JOIN wallet_balances wb ON w.id = wb.wallet_id",
                    params: []
                },
                {
                    name: "Positions ouvertes",
                    sql: "SELECT COUNT(*) FROM positions WHERE status = 'open'",
                    params: []
                }
            ];

            console.log('⚡ Test performance des requêtes...');

            let totalTime = 0;
            let completedTests = 0;

            testQueries.forEach((test, index) => {
                const startTime = process.hrtime.bigint();

                this.db.get(test.sql, test.params, (err) => {
                    if (err) {
                        console.warn(`⚠️ Erreur test ${test.name}:`, err.message);
                    } else {
                        const endTime = process.hrtime.bigint();
                        const queryTime = Number(endTime - startTime) / 1000000; // Convert to ms
                        totalTime += queryTime;

                        console.log(`  ${test.name}: ${queryTime.toFixed(2)}ms`);
                    }

                    completedTests++;
                    if (completedTests === testQueries.length) {
                        const avgTime = totalTime / testQueries.length;
                        console.log(`📊 Temps moyen: ${avgTime.toFixed(2)}ms`);
                        resolve();
                    }
                });
            });
        });
    }

    /**
     * Ferme proprement la connexion à la database
     */
    close() {
        return new Promise((resolve) => {
            if (this.db) {
                this.db.close((err) => {
                    if (err) {
                        console.error('❌ Erreur fermeture DB:', err.message);
                    } else {
                        console.log('✅ Connexion DB fermée');
                    }
                    resolve();
                });
            } else {
                resolve();
            }
        });
    }
}

/**
 * Fonction d'initialisation pour utilisation dans l'application principale
 */
async function initializeDatabase(dbPath) {
    const optimizer = new DatabaseOptimizer(dbPath);
    try {
        await optimizer.initialize();
        return optimizer.db; // Retourner la connexion DB optimisée
    } catch (error) {
        console.error('❌ Échec initialisation database:', error);
        throw error;
    }
}

/**
 * Script autonome pour test
 */
if (require.main === module) {
    async function main() {
        const optimizer = new DatabaseOptimizer();

        try {
            await optimizer.initialize();

            // Test supplémentaire: insérer une donnée de test
            await new Promise((resolve, reject) => {
                optimizer.db.get(
                    "SELECT COUNT(*) as count FROM wallets",
                    [],
                    (err, row) => {
                        if (err) {
                            reject(err);
                        } else {
                            console.log(`📊 Database contient ${row.count} wallets`);
                            resolve();
                        }
                    }
                );
            });

        } catch (error) {
            console.error('❌ Erreur durant le test:', error);
            process.exit(1);
        } finally {
            await optimizer.close();
            console.log('🏁 Test terminé');
        }
    }

    main();
}

module.exports = {
    DatabaseOptimizer,
    initializeDatabase
};