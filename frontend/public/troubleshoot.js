// Diagnostic script for NOVAQUOTE frontend crash debugging
console.log('[DIAGNOSTIC] Initializing crash analysis...');

// Global error handler
window.addEventListener('error', function(e) {
    console.error('[CRASH] JavaScript Error captured:', e.error);
    console.error('[CRASH] Message:', e.message);
    console.error('[CRASH] File:', e.filename);
    console.error('[CRASH] Line:', e.lineno);
    console.error('[CRASH] Column:', e.colno);
    console.error('[CRASH] Stack:', e.error ? e.error.stack : 'No stack');

    // Show alert for user
    alert(`Crash détecté!\n\nErreur: ${e.message}\nFichier: ${e.filename}:${e.lineno}\n\nVérifiez la console pour plus de détails.`);
});

// Global promise rejection handler
window.addEventListener('unhandledrejection', function(e) {
    console.error('[CRASH] Unhandled Promise Rejection:', e.reason);
    console.error('[CRASH] Stack:', e.reason ? e.reason.stack : 'No stack available');

    e.preventDefault(); // Prevent default browser behavior
});

// Check DOM readiness
document.addEventListener('DOMContentLoaded', function() {
    console.log('[DIAGNOSTIC] DOM Content Loaded - checking elements...');

    // Check critical elements existence
    const criticalElements = [
        'walletSelect', 'agentsSummary', 'positionsTable',
        'risk-agent-card', 'strategy-agent-card', 'funding-agent-card', 'sentiment-agent-card'
    ];

    criticalElements.forEach(id => {
        const element = document.getElementById(id);
        if (!element) {
            console.error(`[DIAGNOSTIC] MISSING ELEMENT: ${id}`);
        } else {
            console.log(`[DIAGNOSTIC] ✓ Element ${id} found`);
        }
    });

    // Check if functions exist
    const criticalFunctions = [
        'toggleAgent', 'toggleAllAgents', 'refreshAgentInferences',
        'loadWalletData', 'loadPositions', 'loadActivityTimeline',
        'startAutoRefresh', 'updateMasterControlPanel'
    ];

    criticalFunctions.forEach(funcName => {
        if (typeof window[funcName] !== 'function') {
            console.error(`[DIAGNOSTIC] MISSING FUNCTION: ${funcName}`);
        } else {
            console.log(`[DIAGNOSTIC] ✓ Function ${funcName} found`);
        }
    });
});

// Network error detection
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args)
            .catch(error => {
                console.error('[NETWORK] Fetch error:', error, 'URL:', args[0]);
                throw error;
            });
    };
})();

// Check WebSocket functionality
function testWebSocketConnection() {
    console.log('[DIAGNOSTIC] Testing WebSocket connection...');

    try {
        const ws = new WebSocket('ws://localhost:7001');

        ws.onopen = () => {
            console.log('[DIAGNOSTIC] ✓ WebSocket connection successful');
            ws.close();
        };

        ws.onerror = (error) => {
            console.error('[DIAGNOSTIC] ✗ WebSocket connection failed:', error);
        };

        ws.onclose = (event) => {
            console.log(`[DIAGNOSTIC] WebSocket closed: ${event.code} ${event.reason}`);
        };

        setTimeout(() => {
            if (ws.readyState === WebSocket.CONNECTING) {
                console.error('[DIAGNOSTIC] WebSocket connection timeout');
                ws.close();
            }
        }, 3000);

    } catch (error) {
        console.error('[DIAGNOSTIC] WebSocket creation failed:', error);
    }
}

// Check API endpoints
async function testAPIEndpoints() {
    console.log('[DIAGNOSTIC] Testing API endpoints...');

    const endpoints = [
        '/api/health',
        '/api/wallet',
        '/api/positions',
        '/api/agents/status',
        '/api/trading/auto/status'
    ];

    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`http://localhost:7000${endpoint}`, {
                timeout: 5000
            });

            if (response.ok) {
                console.log(`[DIAGNOSTIC] ✓ API ${endpoint}: ${response.status}`);
            } else {
                console.error(`[DIAGNOSTIC] ✗ API ${endpoint}: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            console.error(`[DIAGNOSTIC] ✗ API ${endpoint} failed:`, error.message);
        }
    }
}

// Run diagnostics after page load
window.addEventListener('load', function() {
    console.log('[DIAGNOSTIC] Page loaded, running diagnostics...');

    setTimeout(() => {
        testWebSocketConnection();
        testAPIEndpoints();
    }, 1000);

    console.log('[DIAGNOSTIC] Diagnostic complete. Check console for errors.');
});
