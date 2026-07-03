function renderHITLBadge(hitl) {
    if (!hitl) return '';
    const niveau = (hitl.niveau || 'VERT').toLowerCase();
    const raison = hitl.raison || '';
    const validateur = hitl.validateur_recommande || '';
    const requis = hitl.requis ? 'Validation requise' : 'Aucune validation requise';

    return `
        <div class="hitl-badge ${niveau}">
            <strong>HITL ${hitl.niveau || 'VERT'}</strong>
            <span class="hitl-raison">${escapeHtml(raison)}</span>
            <span class="hitl-raison">| ${escapeHtml(requis)}${validateur && validateur !== 'Aucun' ? ' — ' + escapeHtml(validateur) : ''}</span>
        </div>
    `;
}

function renderResumeDossier(dossier) {
    if (!dossier) return '<p class="result-value">Aucun résumé disponible.</p>';
    const fields = [
        ['Entreprise', dossier.entreprise],
        ['Profil', dossier.profil],
        ['Activité', dossier.activite],
        ['Objet de la demande', dossier.objet_demande],
    ];
    let html = '';
    for (const [label, value] of fields) {
        if (value) {
            html += `<div class="result-section"><div class="result-label">${label}</div><div class="result-value">${escapeHtml(value)}</div></div>`;
        }
    }
    if (dossier.documents_analyses && dossier.documents_analyses.length > 0) {
        html += `<div class="result-section"><div class="result-label">Documents analysés</div><ul class="result-list">`;
        for (const doc of dossier.documents_analyses) {
            html += `<li>${escapeHtml(doc)}</li>`;
        }
        html += `</ul></div>`;
    }
    if (dossier.pieces_detectees && dossier.pieces_detectees.length > 0) {
        html += `<div class="result-section"><div class="result-label">Pièces présentes</div><ul class="result-list">`;
        for (const piece of dossier.pieces_detectees) {
            html += `<li>${escapeHtml(piece)}</li>`;
        }
        html += `</ul></div>`;
    }
    return html || '<p class="result-value">Aucune information extraite.</p>';
}

function renderPiecesManquantes(pieces) {
    if (!pieces || pieces.length === 0) return '<p class="result-value">Aucune pièce manquante détectée.</p>';
    let html = '<ul class="result-list">';
    for (const piece of pieces) {
        html += `<li class="bold">${escapeHtml(piece)}</li>`;
    }
    html += '</ul>';
    return html;
}

function renderIncoherences(incoherences) {
    if (!incoherences || incoherences.length === 0) return '<p class="result-value">Aucune incohérence détectée.</p>';
    let html = '<ul class="result-list">';
    for (const inc of incoherences) {
        html += `<li class="bold">${escapeHtml(inc)}</li>`;
    }
    html += '</ul>';
    return html;
}

function renderConditions(conditions) {
    const remplies = conditions.conditions_remplies || [];
    const nonRemplies = conditions.conditions_non_remplies || [];
    const nonVerifiables = conditions.conditions_non_verifiables || [];
    const risques = conditions.risques || [];
    const observations = conditions.observations || [];

    let html = '';

    if (remplies.length > 0) {
        html += '<div class="result-section"><div class="result-label" style="color: #27AE60;">✅ Conditions remplies</div><ul class="result-list">';
        for (const c of remplies) html += `<li>${escapeHtml(c)}</li>`;
        html += '</ul></div>';
    }

    if (nonRemplies.length > 0) {
        html += '<div class="result-section"><div class="result-label" style="color: #C0392B;">❌ Conditions non remplies</div><ul class="result-list">';
        for (const c of nonRemplies) html += `<li>${escapeHtml(c)}</li>`;
        html += '</ul></div>';
    }

    if (nonVerifiables.length > 0) {
        html += '<div class="result-section"><div class="result-label" style="color: #E67E22;">⚠️ Conditions non vérifiables</div><ul class="result-list">';
        for (const c of nonVerifiables) html += `<li>${escapeHtml(c)}</li>`;
        html += '</ul></div>';
    }

    if (risques.length > 0) {
        html += '<div class="result-section"><div class="result-label" style="color: #C0392B;">🔴 Risques</div><ul class="result-list">';
        for (const r of risques) html += `<li>${escapeHtml(r)}</li>`;
        html += '</ul></div>';
    }

    if (observations.length > 0) {
        html += '<div class="result-section"><div class="result-label">📝 Observations</div><ul class="result-list">';
        for (const o of observations) html += `<li>${escapeHtml(o)}</li>`;
        html += '</ul></div>';
    }

    return html || '<p class="result-value">Aucune condition analysée.</p>';
}

function renderRAGResults(results) {
    if (!results || results.length === 0) return '<p class="result-value">Aucun résultat RAG vectoriel.</p>';
    let html = '';
    for (const r of results) {
        html += `
            <div class="rag-result">
                <div class="rag-section">${escapeHtml(r.section || 'Section inconnue')} — ${escapeHtml(r.source || '')}</div>
                <div class="rag-extrait">${escapeHtml((r.extrait || '').substring(0, 300))}${r.extrait && r.extrait.length > 300 ? '...' : ''}</div>
                ${r.utilite ? `<div class="rag-extrait" style="margin-top:4px;font-style:italic;color:#A0785A;">${escapeHtml(r.utilite)}</div>` : ''}
            </div>
        `;
    }
    return html;
}

function renderGraphRAGPaths(paths) {
    if (!paths || paths.length === 0) return '<p class="result-value">Aucun chemin GraphRAG trouvé.</p>';
    let html = '';
    for (const p of paths) {
        const chemin = p.chemin || '';
        const parts = chemin.split(' -> ');
        let pathHtml = '';
        for (let i = 0; i < parts.length; i++) {
            if (i > 0) pathHtml += '<span class="path-arrow">→</span>';
            pathHtml += escapeHtml(parts[i].trim());
        }
        html += `
            <div class="graph-path">
                <div class="path-text">${pathHtml}</div>
                ${p.interpretation ? `<div class="path-interpretation">${escapeHtml(p.interpretation)}</div>` : ''}
            </div>
        `;
    }
    return html;
}

const NODE_TYPE_COLORS = {
    'aide': '#27AE60',
    'autorisation': '#8B5E3C',
    'recours': '#E67E22',
    'condition': '#3498DB',
    'piecejustificative': '#9B59B6',
    'niveauhitl': '#C0392B',
    'procedure': '#1ABC9C',
    'document': '#7F8C8D',
    'default': '#A0785A',
};

function _getNodeColor(nodeLabel) {
    const lower = (nodeLabel || '').toLowerCase();
    for (const [key, color] of Object.entries(NODE_TYPE_COLORS)) {
        if (key !== 'default' && lower.includes(key)) return color;
    }
    return NODE_TYPE_COLORS.default;
}

function renderGraphViz(paths) {
    if (!paths || paths.length === 0) return '';

    const nodes = [];
    const nodeMap = {};
    const edges = [];

    for (const p of paths) {
        const nodeLabels = (p.chemin || '').split(' -> ').map(s => s.trim());
        const nodeIds = p.noeuds || [];
        const relations = p.relations || [];

        for (let i = 0; i < nodeLabels.length; i++) {
            const label = nodeLabels[i];
            const id = nodeIds[i] || label;
            if (!nodeMap[id]) {
                nodeMap[id] = { id, label, index: nodes.length };
                nodes.push(nodeMap[id]);
            }
        }

        for (let i = 0; i < nodeIds.length - 1; i++) {
            const src = nodeIds[i] || nodeLabels[i];
            const tgt = nodeIds[i + 1] || nodeLabels[i + 1];
            const rel = relations[i] || '';
            edges.push({ source: src, target: tgt, label: rel });
        }
    }

    if (nodes.length === 0) return '';

    const W = 700;
    const H = Math.max(300, nodes.length * 60 + 40);
    const centerX = W / 2;
    const centerY = H / 2;

    const positions = [];
    if (nodes.length <= 4) {
        const radius = Math.min(W, H) / 2 - 60;
        for (let i = 0; i < nodes.length; i++) {
            const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
            positions.push({
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
            });
        }
    } else {
        const cols = Math.ceil(Math.sqrt(nodes.length));
        const rows = Math.ceil(nodes.length / cols);
        const colSpacing = (W - 120) / Math.max(cols - 1, 1);
        const rowSpacing = (H - 80) / Math.max(rows - 1, 1);
        for (let i = 0; i < nodes.length; i++) {
            const col = i % cols;
            const row = Math.floor(i / cols);
            positions.push({
                x: 60 + col * colSpacing,
                y: 40 + row * rowSpacing,
            });
        }
    }

    let svg = `<svg class="graph-viz-svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`;
    svg += `<defs><marker id="gv-arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#A0785A"/></marker></defs>`;

    for (const edge of edges) {
        const srcNode = nodeMap[edge.source];
        const tgtNode = nodeMap[edge.target];
        if (!srcNode || !tgtNode) continue;
        const srcPos = positions[srcNode.index];
        const tgtPos = positions[tgtNode.index];
        if (!srcPos || !tgtPos) continue;

        const dx = tgtPos.x - srcPos.x;
        const dy = tgtPos.y - srcPos.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 1) continue;
        const offset = 22;
        const endX = tgtPos.x - (dx / dist) * offset;
        const endY = tgtPos.y - (dy / dist) * offset;

        const midX = (srcPos.x + endX) / 2;
        const midY = (srcPos.y + endY) / 2;

        svg += `<line class="gv-edge" x1="${srcPos.x}" y1="${srcPos.y}" x2="${endX}" y2="${endY}"/>`;
        if (edge.label) {
            svg += `<text class="gv-edge-label" x="${midX}" y="${midY - 4}">${escapeHtml(edge.label)}</text>`;
        }
    }

    for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        const pos = positions[i];
        const color = _getNodeColor(node.label);
        const labelShort = node.label.length > 20 ? node.label.substring(0, 18) + '…' : node.label;

        svg += `<g class="gv-node" transform="translate(${pos.x},${pos.y})">`;
        svg += `<circle class="gv-node-circle" r="20" fill="${color}" fill-opacity="0.15" stroke="${color}"/>`;
        svg += `<text class="gv-node-label" y="4" fill="${color}">${escapeHtml(labelShort)}</text>`;
        svg += `</g>`;
    }

    svg += `</svg>`;

    const usedTypes = new Set();
    for (const node of nodes) {
        const lower = node.label.toLowerCase();
        for (const [key] of Object.entries(NODE_TYPE_COLORS)) {
            if (key !== 'default' && lower.includes(key)) {
                usedTypes.add(key);
                break;
            }
        }
    }

    let legend = '<div class="graph-viz-legend">';
    const typeLabels = {
        aide: 'Aide', autorisation: 'Autorisation', recours: 'Recours',
        condition: 'Condition', piecejustificative: 'Pièce',
        niveauhitl: 'HITL', procedure: 'Procédure', document: 'Document',
    };
    for (const type of usedTypes) {
        legend += `<div class="graph-viz-legend-item"><span class="graph-viz-legend-dot" style="background:${NODE_TYPE_COLORS[type]}"></span>${typeLabels[type] || type}</div>`;
    }
    legend += '</div>';

    return svg + legend;
}

function renderRecommandation(rec) {
    if (!rec) return '<p class="result-value">Aucune recommandation.</p>';
    const confiance = rec.niveau_confiance || 0;
    const confianceClass = getConfidenceClass(confiance);
    const decisionLabels = {
        'demande_de_complement': 'Demande de complément',
        'instruction_possible': 'Instruction possible',
        'escalade': 'Escalade',
        'rejet_potentiel': 'Rejet potentiel',
        'analyse_impossible': 'Analyse impossible',
    };
    const decisionLabel = decisionLabels[rec.decision_proposee] || rec.decision_proposee || 'Inconnu';

    return `
        <div class="result-section">
            <div class="result-label">Décision proposée</div>
            <div class="result-value" style="font-weight:600;font-size:16px;color:${getConfidenceColor(confiance)};">${escapeHtml(decisionLabel)}</div>
        </div>
        <div class="result-section">
            <div class="result-label">Niveau de confiance</div>
            <div class="confidence-bar"><div class="confidence-fill ${confianceClass}" style="width:${confiance * 100}%"></div></div>
            <div class="confidence-value">${(confiance * 100).toFixed(1)}%</div>
        </div>
        ${rec.justification ? `<div class="result-section"><div class="result-label">Justification</div><div class="result-value">${escapeHtml(rec.justification)}</div></div>` : ''}
    `;
}

function renderTypeBadge(typeDemande) {
    const type = (typeDemande || 'inconnu').toLowerCase();
    return `<span class="type-badge ${type}">${escapeHtml(type)}</span>`;
}

function renderTimeline(traces) {
    if (!traces || traces.length === 0) return "<p class=\"result-value\">Aucune trace d'exécution.</p>";
    let html = '<div class="timeline">';
    for (const t of traces) {
        const status = t.status || 'success';
        const icon = status === 'success' ? '✓' : (status === 'warning' ? '!' : '✗');
        html += `
            <div class="timeline-item">
                <div class="timeline-dot ${status}">${icon}</div>
                <div class="timeline-content">
                    <div class="timeline-node-name">${escapeHtml(t.node_name || '')}</div>
                    <div class="timeline-meta">${t.duration_ms || 0}ms — ${status}</div>
                    ${t.input_summary ? `<div class="timeline-meta">In: ${escapeHtml(t.input_summary)}</div>` : ''}
                    ${t.output_summary ? `<div class="timeline-meta">Out: ${escapeHtml(t.output_summary)}</div>` : ''}
                </div>
            </div>
        `;
    }
    html += '</div>';
    return html;
}

function renderVulnerabilities(vulns) {
    if (!vulns || vulns.length === 0) return '<p class="result-value">Aucune vulnérabilité documentée.</p>';
    let html = '<ul class="result-list">';
    for (const v of vulns) {
        html += `<li>${escapeHtml(v)}</li>`;
    }
    html += '</ul>';
    return html;
}

function renderDebugQueries(finalJson) {
    let html = '';
    if (finalJson.vector_query) {
        html += `<div class="result-section"><div class="result-label">Requête vectorielle</div><div class="result-value" style="font-family:monospace;font-size:12px;">${escapeHtml(finalJson.vector_query)}</div></div>`;
    }
    if (finalJson.graph_query) {
        html += `<div class="result-section"><div class="result-label">Requête GraphRAG</div><div class="result-value" style="font-family:monospace;font-size:12px;">${escapeHtml(finalJson.graph_query)}</div></div>`;
    }
    return html || '<p class="result-value">Aucune requête interne disponible.</p>';
}
