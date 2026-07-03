let selectedFiles = [];
let debugMode = false;

const WORKFLOW_STEPS = [
    'node_receive_input',
    'node_validate_input_basic',
    'node_extract_files',
    'node_build_temporary_dossier_summary',
    'node_classify_admin_request',
    'node_build_vector_query',
    'node_vector_retrieve',
    'node_build_graph_query',
    'node_graph_retrieve_paths',
    'node_merge_contexts',
    'node_administrative_analysis_llm',
    'node_parse_and_validate_json',
    'node_hitl_router',
    'node_clean_response_for_frontend',
    'node_persist_run_logs',
];

const STEP_LABELS = {
    'node_receive_input': 'Réception de la question',
    'node_validate_input_basic': 'Validation des entrées',
    'node_extract_files': 'Extraction des fichiers',
    'node_build_temporary_dossier_summary': 'Résumé du dossier',
    'node_classify_admin_request': 'Classification de la demande',
    'node_build_vector_query': 'Construction requête vectorielle',
    'node_vector_retrieve': 'Recherche RAG vectoriel',
    'node_build_graph_query': 'Construction requête GraphRAG',
    'node_graph_retrieve_paths': 'Recherche GraphRAG multi-hop',
    'node_merge_contexts': 'Fusion des contextes',
    'node_administrative_analysis_llm': 'Analyse administrative LLM',
    'node_parse_and_validate_json': 'Validation JSON',
    'node_hitl_router': 'Routage HITL',
    'node_clean_response_for_frontend': 'Nettoyage de la réponse',
    'node_persist_run_logs': 'Persistance des logs',
};

document.addEventListener('DOMContentLoaded', () => {
    initDropzone();
    initFileInput();
    initAnalyzeButton();
    initDebugToggle();
    initCopyJson();
    updateAnalyzeButton();
});

function initDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
}

function initFileInput() {
    const fileInput = document.getElementById('file-input');
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });
}

function handleFiles(fileList) {
    for (const file of fileList) {
        selectedFiles.push(file);
    }
    renderFileList();
    updateAnalyzeButton();
}

function renderFileList() {
    const container = document.getElementById('file-list');
    container.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span class="file-name">${escapeHtml(file.name)}</span>
            <span class="file-size">${formatBytes(file.size)}</span>
            <span class="file-remove" data-index="${index}">&times;</span>
        `;
        container.appendChild(item);
    });

    container.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = parseInt(e.target.dataset.index);
            selectedFiles.splice(idx, 1);
            renderFileList();
            updateAnalyzeButton();
        });
    });
}

function updateAnalyzeButton() {
    const btn = document.getElementById('analyze-btn');
    const question = document.getElementById('question').value.trim();
    btn.disabled = !question && selectedFiles.length === 0;
}

document.getElementById('question').addEventListener('input', updateAnalyzeButton);

function initAnalyzeButton() {
    const btn = document.getElementById('analyze-btn');
    btn.addEventListener('click', runAnalysis);
}

function initDebugToggle() {
    const btn = document.getElementById('debug-toggle');
    btn.addEventListener('click', () => {
        debugMode = !debugMode;
        btn.classList.toggle('active', debugMode);
        const debugSection = document.getElementById('debug-section');
        debugSection.classList.toggle('hidden', !debugMode);
    });
}

function initCopyJson() {
    const btn = document.getElementById('copy-json-btn');
    btn.addEventListener('click', () => {
        const jsonText = document.getElementById('json-viewer').textContent;
        copyToClipboard(jsonText);
    });
}

async function runAnalysis() {
    const question = document.getElementById('question').value.trim();
    const typeDossier = document.getElementById('type-dossier').value;
    const identifiantDossier = document.getElementById('identifiant-dossier').value;

    if (!question && selectedFiles.length === 0) return;

    showLoading();
    renderLoadingSteps();

    try {
        const result = await analyzeDossier(question, typeDossier, identifiantDossier, selectedFiles);
        hideLoading();
        renderResults(result);
    } catch (error) {
        hideLoading();
        showError(error.message, 'Vérifiez que le backend est démarré et accessible.');
    }
}

function showLoading() {
    document.getElementById('loading-section').classList.remove('hidden');
    document.getElementById('error-section').classList.add('hidden');
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('analyze-btn').disabled = true;
}

function hideLoading() {
    document.getElementById('loading-section').classList.add('hidden');
    document.getElementById('analyze-btn').disabled = false;
}

function renderLoadingSteps() {
    const container = document.getElementById('loading-steps');
    container.innerHTML = '';
    WORKFLOW_STEPS.forEach((step, i) => {
        const el = document.createElement('div');
        el.className = 'loading-step';
        el.id = `loading-step-${i}`;
        el.textContent = STEP_LABELS[step] || step;
        container.appendChild(el);

        setTimeout(() => {
            const prev = document.getElementById(`loading-step-${i - 1}`);
            if (prev) prev.classList.add('done');
            const status = document.getElementById('loading-status');
            if (status) status.textContent = STEP_LABELS[step] || step;
        }, i * 400);
    });
}

function showError(message, suggestion) {
    const section = document.getElementById('error-section');
    section.classList.remove('hidden');
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-suggestion').textContent = suggestion || '';
}

function renderResults(result) {
    const section = document.getElementById('results-section');
    section.classList.remove('hidden');

    const cleaned = result.cleaned_response || {};
    const finalJson = result.final_json || {};
    const traces = result.debug_trace || [];
    const errors = result.errors || [];

    document.getElementById('run-id').textContent = result.run_id || 'N/A';
    document.getElementById('run-duration').textContent = `${result.total_duration_ms || 0}ms`;

    const hitlContainer = document.getElementById('hitl-badge-container');
    hitlContainer.innerHTML = renderHITLBadge(cleaned.hitl || finalJson.hitl);

    document.getElementById('resume-content').innerHTML = renderResumeDossier(cleaned.resume_dossier || finalJson.resume_dossier_temporaire);

    const typeContent = document.getElementById('type-content');
    typeContent.innerHTML = `<div style="padding:16px 0;">${renderTypeBadge(cleaned.type_demande || finalJson.type_demande)}</div>`;

    const piecesManquantes = (cleaned.resume_dossier || {}).pieces_manquantes || (finalJson.resume_dossier_temporaire || {}).pieces_manquantes || [];
    const piecesCard = document.getElementById('card-pieces-manquantes');
    if (piecesManquantes.length > 0) {
        piecesCard.classList.remove('hidden');
        document.getElementById('pieces-manquantes-content').innerHTML = renderPiecesManquantes(piecesManquantes);
    } else {
        piecesCard.classList.add('hidden');
    }

    const incoherences = (cleaned.resume_dossier || {}).incoherences_detectees || (finalJson.resume_dossier_temporaire || {}).incoherences_detectees || [];
    const incoherencesCard = document.getElementById('card-incoherences');
    if (incoherences.length > 0) {
        incoherencesCard.classList.remove('hidden');
        document.getElementById('incoherences-content').innerHTML = renderIncoherences(incoherences);
    } else {
        incoherencesCard.classList.add('hidden');
    }

    document.getElementById('conditions-content').innerHTML = renderConditions({
        conditions_remplies: cleaned.conditions_remplies,
        conditions_non_remplies: cleaned.conditions_non_remplies,
        conditions_non_verifiables: cleaned.conditions_non_verifiables,
        risques: cleaned.risques,
        observations: cleaned.observations,
    });

    document.getElementById('rag-content').innerHTML = renderRAGResults(cleaned.resultats_rag_vectoriel || finalJson.resultats_rag_vectoriel);
    document.getElementById('graphrag-content').innerHTML = renderGraphRAGPaths(cleaned.resultats_graphrag || finalJson.resultats_graphrag);
    document.getElementById('recommandation-content').innerHTML = renderRecommandation(cleaned.recommandation || finalJson.recommandation);

    const reponseText = cleaned.reponse_proposee || finalJson.reponse_proposee_a_l_administrateur || '';
    document.getElementById('reponse-content').innerHTML = `<div class="response-text">${escapeHtml(reponseText)}</div>`;

    if (debugMode) {
        document.getElementById('debug-queries-content').innerHTML = renderDebugQueries(finalJson);
        document.getElementById('debug-vulnerabilities-content').innerHTML = renderVulnerabilities(cleaned.vulnerabilites_v1_connues || finalJson.vulnerabilites_v1_connues);
    }

    document.getElementById('json-viewer').innerHTML = syntaxHighlightJSON(finalJson);
    document.getElementById('timeline-content').innerHTML = renderTimeline(traces);

    section.scrollIntoView({ behavior: 'smooth' });
}
