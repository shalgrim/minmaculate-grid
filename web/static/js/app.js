// Minmaculate Grid - Frontend Application

// API Base URL
const API_BASE = '/api';

// Global state
let currentSolutionId = null;
let allFranchises = [];
let allSolutions = [];

// Utility: Fetch wrapper with error handling
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showError(`Failed to fetch data: ${error.message}`);
        throw error;
    }
}

// Show error message
function showError(message) {
    console.error(message);
    // Could add toast notification here
}

// Initialize app
async function init() {
    try {
        await loadSolutions();
        await loadFranchises();
        setupEventListeners();
        await loadCoverageHeatmap();
    } catch (error) {
        console.error('Initialization error:', error);
    }
}

// Load and display solutions comparison
async function loadSolutions() {
    const solutions = await fetchAPI('/solutions');
    allSolutions = solutions;
    displaySolutionsTable(solutions);

    // Populate solution selector
    const selector = document.getElementById('solution-selector');
    selector.innerHTML = solutions.map(s =>
        `<option value="${s.id}">${s.algorithm.toUpperCase()} (${s.num_players} players)</option>`
    ).join('');

    // Auto-select first solution
    if (solutions.length > 0) {
        currentSolutionId = solutions[0].id;
        selector.value = currentSolutionId;
        await loadSolutionDetail(currentSolutionId);
    }
}

// Display solutions comparison table
function displaySolutionsTable(solutions) {
    // Find the best (minimum) solution
    const minPlayers = Math.min(...solutions.map(s => s.num_players));

    const html = `
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>Algorithm</th>
                    <th>Players</th>
                    <th>Runtime</th>
                    <th>Coverage</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${solutions.map(s => {
                    const isBest = s.num_players === minPlayers;
                    return `
                        <tr class="${isBest ? 'solution-best' : ''}">
                            <td><strong>${s.algorithm.toUpperCase()}</strong></td>
                            <td>${s.num_players} ${isBest ? '✅' : ''}</td>
                            <td>${s.runtime_seconds.toFixed(2)}s</td>
                            <td>${s.coverage_percentage.toFixed(1)}%</td>
                            <td>${isBest ? '<span class="badge bg-success">Optimal</span>' : '<span class="badge bg-secondary">Approximation</span>'}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;

    document.getElementById('solutions-table').innerHTML = html;

    // Add comparison info if we have both greedy and exact
    if (solutions.length >= 2) {
        const greedy = solutions.find(s => s.algorithm === 'greedy');
        const exact = solutions.find(s => s.algorithm === 'exact' || s.algorithm === 'optimal');

        if (greedy && exact) {
            const improvement = greedy.num_players - exact.num_players;
            const ratio = (greedy.num_players / exact.num_players).toFixed(4);

            const comparisonHtml = `
                <div class="alert alert-info mt-3">
                    <strong>Comparison:</strong> The exact solver found a solution ${improvement} player(s) better than greedy.
                    Approximation ratio: ${ratio} (greedy is ${ratio}x the optimal).
                </div>
            `;

            document.getElementById('solutions-table').insertAdjacentHTML('beforeend', comparisonHtml);
        }
    }
}

// Load solution details
async function loadSolutionDetail(solutionId) {
    currentSolutionId = solutionId;
    const solution = await fetchAPI(`/solutions/${solutionId}`);
    displaySolutionPlayers(solution);
}

// Display solution players
function displaySolutionPlayers(solution) {
    const html = `
        <div class="mb-3">
            <h3>${solution.algorithm.toUpperCase()} Solution</h3>
            <p class="text-muted">
                ${solution.num_players} players, ${solution.runtime_seconds.toFixed(2)}s runtime,
                ${solution.coverage_percentage.toFixed(1)}% coverage
            </p>
        </div>

        <div class="row">
            ${solution.players.map(p => `
                <div class="col-md-6 col-lg-4">
                    <div class="player-card">
                        <h5>${p.rank}. ${p.full_name}</h5>
                        <p class="text-muted mb-0">
                            ${p.num_pairs} pairs covered
                        </p>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    document.getElementById('solution-players').innerHTML = html;
}

// Load franchises for dropdowns
async function loadFranchises() {
    const pairs = await fetchAPI('/pairs');
    const franchiseSet = new Set();

    pairs.forEach(p => {
        franchiseSet.add(p.franchise_1);
        franchiseSet.add(p.franchise_2);
    });

    allFranchises = Array.from(franchiseSet).sort();

    // Populate dropdowns
    const options = allFranchises.map(f =>
        `<option value="${f}">${f}</option>`
    ).join('');

    document.getElementById('franchise1').innerHTML = options;
    document.getElementById('franchise2').innerHTML = options;

    // Set different defaults
    if (allFranchises.length > 1) {
        document.getElementById('franchise2').value = allFranchises[1];
    }
}

// Load and display coverage heatmap
async function loadCoverageHeatmap() {
    try {
        const data = await fetchAPI('/coverage-matrix');

        // Create heatmap using Plotly
        const heatmapData = [{
            z: data.matrix,
            x: data.franchises,
            y: data.franchises,
            type: 'heatmap',
            colorscale: [
                [0, '#f0f9ff'],
                [0.5, '#0ea5e9'],
                [1, '#1e3a8a']
            ],
            hovertemplate: '%{y} vs %{x}: %{z} players<extra></extra>',
            showscale: true,
            colorbar: {
                title: 'Players',
                thickness: 15,
                len: 0.7
            }
        }];

        const layout = {
            title: {
                text: 'Player Coverage by Franchise Pair',
                font: { size: 16 }
            },
            xaxis: {
                title: 'Franchise',
                tickangle: -45,
                tickfont: { size: 10 }
            },
            yaxis: {
                title: 'Franchise',
                tickfont: { size: 10 }
            },
            margin: { l: 80, r: 80, t: 80, b: 120 },
            height: 700
        };

        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        };

        Plotly.newPlot('coverageHeatmap', heatmapData, layout, config);
    } catch (error) {
        document.getElementById('coverageHeatmap').innerHTML =
            '<div class="alert alert-warning">Failed to load heatmap. Make sure the database is populated.</div>';
    }
}

// Player search with debouncing
let searchTimeout;
function setupPlayerSearch() {
    const searchInput = document.getElementById('player-search');
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchPlayers(e.target.value);
        }, 300);
    });
}

async function searchPlayers(query) {
    const resultsDiv = document.getElementById('player-results');

    if (query.length < 2) {
        resultsDiv.innerHTML = '';
        return;
    }

    try {
        // Fetch players (with pagination if needed)
        const players = await fetchAPI('/players?limit=1000');

        // Filter client-side
        const filtered = players.filter(p =>
            p.full_name.toLowerCase().includes(query.toLowerCase())
        );

        if (filtered.length === 0) {
            resultsDiv.innerHTML = '<p class="text-muted">No players found.</p>';
            return;
        }

        displayPlayerResults(filtered.slice(0, 20)); // Show top 20
    } catch (error) {
        resultsDiv.innerHTML = '<div class="alert alert-danger">Error searching players.</div>';
    }
}

function displayPlayerResults(players) {
    const html = `
        <div class="border rounded">
            ${players.map(p => `
                <div class="search-result-item" onclick="showPlayerDetail('${p.player_id}')">
                    <strong>${p.full_name}</strong>
                    <span class="text-muted ms-2">• Debut: ${p.debut}</span>
                </div>
            `).join('')}
        </div>
    `;

    document.getElementById('player-results').innerHTML = html;
}

async function showPlayerDetail(playerId) {
    try {
        const player = await fetchAPI(`/players/${playerId}`);

        const html = `
            <div class="player-detail-card">
                <h4>${player.full_name}</h4>
                <p><strong>Debut:</strong> ${player.debut}</p>
                <p><strong>${player.num_pairs}</strong> franchise pairs covered</p>

                <h5 class="mt-3">Franchise Pairs:</h5>
                <div class="pair-list">
                    ${player.pairs_covered.map(p => `
                        <div class="pair-badge">${p.franchise_1} - ${p.franchise_2}</div>
                    `).join('')}
                </div>
            </div>
        `;

        document.getElementById('player-results').innerHTML = html;
    } catch (error) {
        document.getElementById('player-results').innerHTML =
            '<div class="alert alert-danger">Error loading player details.</div>';
    }
}

// Pair lookup
async function lookupPair() {
    const f1 = document.getElementById('franchise1').value;
    const f2 = document.getElementById('franchise2').value;

    if (f1 === f2) {
        alert('Please select two different franchises');
        return;
    }

    try {
        const data = await fetchAPI(`/pairs/${f1}/${f2}`);

        const html = `
            <div class="player-detail-card">
                <h4>${data.franchise_1} vs ${data.franchise_2}</h4>
                <p class="lead"><strong>${data.num_players}</strong> players who played for both teams</p>

                <div class="row mt-3">
                    ${data.players.map(p => `
                        <div class="col-md-4 col-lg-3 mb-3">
                            <div class="player-card" onclick="showPlayerDetail('${p.player_id}')">
                                <h5>${p.full_name}</h5>
                                <p class="text-muted mb-0">
                                    <small>Debut: ${p.debut}</small>
                                </p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        document.getElementById('pair-results').innerHTML = html;
    } catch (error) {
        document.getElementById('pair-results').innerHTML =
            '<div class="alert alert-danger">Error loading franchise pair data.</div>';
    }
}

// Event listeners
function setupEventListeners() {
    document.getElementById('lookup-pair-btn').addEventListener('click', lookupPair);
    document.getElementById('solution-selector').addEventListener('change', (e) => {
        loadSolutionDetail(parseInt(e.target.value));
    });
    setupPlayerSearch();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
