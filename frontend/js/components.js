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

function renderSecurityReport(report) {
    const summary = report.summary || {};
    const guardrail = report.guardrail || {};
    const findings = report.static_findings || [];
    const evidence = report.evidence || [];
    const skillspector = report.skillspector || {};
    const scanReport = report.skillspector_report || {};
    const realSkillSpector = skillspector.report || {};
    const skillRisk = realSkillSpector.risk_assessment || {};
    const skillIssues = realSkillSpector.issues || [];
    const skillComponents = realSkillSpector.components || [];
    const garak = report.garak || {};
    const isSecured = report.mode === 'secured';
    const threatLevel = getHumanThreatLevel(summary, skillRisk, findings, guardrail);
    const protectionState = getProtectionState(isSecured, guardrail);
    const scannerState = getScannerState(skillRisk, skillIssues, threatLevel.score);
    const riskClass = threatLevel.className;

    let findingsHtml = '<p class="result-value">Aucune instruction suspecte détectée dans le texte extrait.</p>';
    if (findings.length > 0) {
        findingsHtml = '<ul class="result-list">';
        for (const item of findings) {
            findingsHtml += `<li><strong>${escapeHtml(humanRuleName(item.rule_id || ''))}</strong><br>${escapeHtml(item.message || '')}</li>`;
        }
        findingsHtml += '</ul>';
    }

    return `
        <div class="security-hero ${riskClass}">
            <div>
                <span class="result-label">Risque du document</span>
                <h3>${escapeHtml(threatLevel.title)}</h3>
                <p>${escapeHtml(threatLevel.message)}</p>
            </div>
            <div class="security-score-ring">
                <strong>${escapeHtml(String(threatLevel.score))}</strong>
                <span>/100</span>
            </div>
        </div>
        <div class="security-summary-row">
            <div class="security-metric ${riskClass}">
                <span>Risque document</span>
                <strong>${escapeHtml(threatLevel.short)}</strong>
            </div>
            <div class="security-metric ${protectionState.className}">
                <span>Protection</span>
                <strong>${escapeHtml(protectionState.title)}</strong>
            </div>
            <div class="security-metric">
                <span>Action</span>
                <strong>${escapeHtml(protectionState.action)}</strong>
            </div>
            <div class="security-metric">
                <span>SkillSpector</span>
                <strong>${escapeHtml(scannerState.status)}</strong>
            </div>
            <div class="security-metric">
                <span>Signaux</span>
                <strong>${escapeHtml(String(skillIssues.length || findings.length || 0))}</strong>
            </div>
        </div>
        <div class="security-bars">
            <div>
                <div class="bar-head"><span>Score de risque document</span><strong>${escapeHtml(String(threatLevel.score))}/100</strong></div>
                <div class="threat-bar"><div class="${riskClass}" style="width:${Math.max(threatLevel.score, 4)}%"></div></div>
            </div>
            <div>
                <div class="bar-head"><span>État de la protection</span><strong>${escapeHtml(protectionState.title)}</strong></div>
                <div class="protection-strip ${protectionState.className}">${escapeHtml(protectionState.message)}</div>
            </div>
        </div>
        <div class="result-section">
            <div class="result-label">ID rapport</div>
            <div class="result-value code-inline">${escapeHtml(report.report_id || '')}</div>
        </div>
        <div class="result-section">
            <div class="result-label">Dossier</div>
            <div class="result-value">${escapeHtml(report.case_id || 'manual_input')}</div>
        </div>
        <div class="result-section">
            <div class="result-label">Verdict</div>
            <div class="result-value bold">${escapeHtml(threatLevel.title)}</div>
            <p>${escapeHtml(threatLevel.message)}</p>
        </div>
        <div class="result-section">
            <div class="result-label">Signaux détectés</div>
            ${findingsHtml}
        </div>
        <div class="result-section">
            <div class="result-label">Extraits justificatifs</div>
            ${renderSecurityEvidence(evidence)}
        </div>
        <div class="result-section">
            <div class="result-label">Décision de protection</div>
            <div class="result-value bold">${escapeHtml(protectionState.action)}</div>
            <p>${escapeHtml(protectionState.message)}</p>
        </div>
        <div class="result-section">
            <div class="result-label">Rapport SkillSpector</div>
            ${renderSkillSpectorDetails(skillRisk, skillIssues, skillComponents, realSkillSpector)}
        </div>
        <div class="result-section">
            <div class="result-label">Recommandation</div>
            <p>${escapeHtml(scanReport.recommendation || protectionState.recommendation)}</p>
        </div>
    `;
}

function getHumanThreatLevel(summary, risk, findings, guardrail) {
    const score = Number(risk.score ?? (findings.length ? 40 : 0));
    if (guardrail?.blocked) {
        return {
            className: 'orange',
            score: Math.max(score, 70),
            short: 'Blocked',
            title: 'Menace détectée et bloquée',
            message: 'Le document contient des consignes qui tentent d influencer le modèle. Le mode sécurisé a arrêté la demande avant l analyse normale.'
        };
    }
    if (score >= 70 || summary.level === 'high') {
        return {
            className: 'red',
            score: Math.max(score, 80),
            short: 'Élevé',
            title: 'Document à risque élevé',
            message: 'Le document contient des instructions suspectes capables de manipuler le modèle si elles sont traitées sans protection.'
        };
    }
    if (score > 0 || findings.length > 0 || summary.level === 'medium') {
        return {
            className: 'orange',
            score: Math.max(score, 50),
            short: 'Suspect',
            title: 'Contenu suspect détecté',
            message: 'Le scan a trouvé des indicateurs de prompt injection. Utiliser le mode sécurisé avant l analyse normale.'
        };
    }
    return {
        className: 'green',
        score: 0,
        short: 'Propre',
        title: 'Aucune instruction malveillante détectée',
        message: 'Le texte extrait ne contient pas de motif connu de prompt injection ou d exfiltration.'
    };
}

function getProtectionState(isSecured, guardrail) {
    if (!isSecured) {
        return {
            className: 'orange',
            title: 'Non appliquée',
            action: 'Observation seule',
            message: 'Le mode non sécurisé ne bloque rien. Il affiche seulement ce que le scanner observe.',
            recommendation: 'Relancer le même dossier en mode sécurisé pour appliquer le blocage automatique.'
        };
    }
    if (guardrail?.blocked) {
        return {
            className: 'green',
            title: 'Active',
            action: 'Bloqué',
            message: 'Le mode sécurisé a bloqué le contenu suspect avant qu il influence l analyse.',
            recommendation: 'Conserver le blocage et envoyer le dossier en revue manuelle.'
        };
    }
    return {
        className: 'green',
        title: 'Active',
        action: 'Autorisé',
        message: 'Le mode sécurisé a contrôlé l entrée et l a autorisée car aucune règle bloquante n a été déclenchée.',
        recommendation: 'Continuer l analyse normale du dossier.'
    };
}

function getScannerState(risk, issues, threatScore) {
    const score = Number(risk.score ?? threatScore ?? 0);
    const severity = risk.severity || (score ? 'MEDIUM' : 'LOW');
    const recommendation = risk.recommendation || (score ? 'CAUTION' : 'SAFE');
    return {
        score,
        label: recommendation,
        status: `${severity} / ${recommendation}`,
    };
}

function humanRuleName(ruleId) {
    const names = {
        instruction_override: 'Tentative d annulation des règles',
        system_instruction_block: 'Instruction cachée de type système',
        policy_bypass: 'Tentative de contournement de politique',
        system_prompt_request: 'Demande du prompt système',
        secret_exfiltration: 'Tentative d extraction de secret',
        tool_abuse: 'Tentative d abus d outil',
        network_exfiltration: 'Tentative d exfiltration réseau',
    };
    return names[ruleId] || ruleId;
}

function renderSkillSpectorDetails(risk, issues, components, rawReport) {
    if (!rawReport || Object.keys(rawReport).length === 0) {
        return '<p class="result-value">SkillSpector n a pas retourné de rapport complet pour cette exécution.</p>';
    }
    let html = `
        <div class="security-summary-row compact">
            <div class="security-metric">
                <span>Score scanner</span>
                <strong>${escapeHtml(String(risk.score ?? '0'))}/100</strong>
            </div>
            <div class="security-metric">
                <span>Sévérité scanner</span>
                <strong>${escapeHtml(risk.severity || 'LOW')}</strong>
            </div>
            <div class="security-metric">
                <span>Avis scanner</span>
                <strong>${escapeHtml(risk.recommendation || 'SAFE')}</strong>
            </div>
            <div class="security-metric">
                <span>Problèmes</span>
                <strong>${escapeHtml(String(issues.length))}</strong>
            </div>
        </div>
        <p>SkillSpector a scanné ${escapeHtml(components.length)} composant(s) généré(s): ${escapeHtml(components.map(c => c.path).join(', ') || 'aucun')}.</p>
    `;
    if (issues.length > 0) {
        html += '<ul class="result-list">';
        for (const issue of issues) {
            html += `<li><strong>${escapeHtml(issue.severity || '')}</strong> - ${escapeHtml(issue.category || '')}: ${escapeHtml(issue.pattern || issue.finding || '')}<br>${escapeHtml(issue.explanation || '')}</li>`;
        }
        html += '</ul>';
    } else {
        html += '<p class="result-value">SkillSpector n a trouvé aucun motif dangereux dans le snapshot généré pour ce dossier.</p>';
    }
    return html;
}

function renderSecurityEvidence(evidence) {
    if (!evidence || evidence.length === 0) {
        return '<p class="result-value">Aucun extrait suspect extrait.</p>';
    }
    let html = '<ul class="result-list">';
    for (const item of evidence) {
        html += `<li><strong>${escapeHtml(item.rule_id || '')}</strong> - ${escapeHtml(item.snippet || '')}</li>`;
    }
    html += '</ul>';
    return html;
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
