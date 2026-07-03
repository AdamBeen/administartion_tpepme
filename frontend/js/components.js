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
