const API_BASE = window.location.origin;

async function analyzeDossier(question, typeDossier, identifiantDossier, files) {
    const formData = new FormData();
    formData.append('question', question);
    formData.append('type_dossier', typeDossier);
    formData.append('identifiant_dossier', identifiantDossier || '');

    for (const file of files) {
        formData.append('files', file);
    }

    const response = await fetch(`${API_BASE}/api/analyze`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        return response.json();
    } catch {
        return { status: 'error', astra_db: false, config_errors: ['API unreachable'] };
    }
}
