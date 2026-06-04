function setupText(value, fallback = "-") {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
}

function setupList(values, className = "setup-chip") {
    if (!values || values.length === 0) {
        return '<span class="setup-muted">None configured</span>';
    }
    return values.map(value => `<span class="${className}">${escapeHtml(setupText(value))}</span>`).join("");
}

function escapeHtml(value) {
    return setupText(value, "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    }[char]));
}

function actionClass(action) {
    const normalized = setupText(action, "").toLowerCase();
    if (normalized === "drop") return "setup-badge-danger";
    if (normalized === "consider") return "setup-badge-warning";
    if (normalized === "reserve") return "setup-badge-purple";
    if (normalized === "true" || normalized === "boost") return "setup-badge-success";
    return "setup-badge-neutral";
}

function renderSetupSection(title, icon, bodyHtml) {
    return `
        <article class="card setup-card">
            <div class="setup-card-header">
                <span class="material-icons-outlined">${icon}</span>
                <h3>${escapeHtml(title)}</h3>
            </div>
            ${bodyHtml}
        </article>
    `;
}

function renderKeyValueRows(items) {
    return `
        <div class="setup-kv-list">
            ${items.map(item => `
                <div class="setup-kv-row">
                    <span>${escapeHtml(item.label)}</span>
                    <strong>${escapeHtml(item.value)}</strong>
                </div>
            `).join("")}
        </div>
    `;
}

function renderSetupTab(memory) {
    const root = document.getElementById("setup-root");
    if (!root) return;

    if (!memory) {
        root.innerHTML = `
            <div class="empty-state">
                <span class="material-icons-outlined empty-icon">settings_suggest</span>
                <h2>No Setup Loaded</h2>
                <p>Select an app to view its project memory.</p>
            </div>
        `;
        return;
    }

    const identity = memory.identity || {};
    const positioning = memory.positioning || {};
    const keywordSetup = memory.keyword_setup || {};
    const competitorSetup = memory.competitor_setup || {};
    const riskSetup = memory.risk_setup || {};
    const riskGroups = riskSetup.groups || {};
    const warnings = memory.warnings || [];
    const competitors = competitorSetup.competitor_apps || [];

    root.innerHTML = `
        <div class="setup-hero card">
            <div>
                <div class="setup-eyebrow">Project Memory</div>
                <h2>${escapeHtml(identity.app_name || "Unknown app")}</h2>
                <p>${escapeHtml(identity.app_id || "")}</p>
            </div>
            <div class="setup-hero-meta">
                <span class="setup-badge setup-badge-neutral">${escapeHtml(identity.market || "No market")}</span>
                <span class="setup-badge setup-badge-neutral">${escapeHtml(identity.semantic_mode || "No semantic mode")}</span>
                <span class="setup-badge setup-badge-success">Updated ${escapeHtml(memory.generated_at || "")}</span>
            </div>
        </div>

        <div class="setup-grid">
            ${renderSetupSection("Identity", "badge", renderKeyValueRows([
                { label: "Category", value: setupText(identity.category) },
                { label: "Platform", value: setupText(identity.platform_mode) },
                { label: "Config source", value: setupText(memory.config_source) },
                { label: "Profile status", value: setupText(positioning.profile_status) }
            ]))}

            ${renderSetupSection("Positioning", "flag", `
                <div class="setup-copy-block">
                    <strong>${escapeHtml(positioning.store_title || identity.app_name || "")}</strong>
                    <p>${escapeHtml(positioning.short_description || "No short description available.")}</p>
                    <p>${escapeHtml(positioning.primary_positioning || positioning.full_description_summary || "")}</p>
                </div>
                <div class="setup-chip-group">${setupList(positioning.strongest_differentiators || [])}</div>
            `)}

            ${renderSetupSection("Keyword Setup", "sell", `
                <div class="setup-term-group"><label>Core terms</label><div>${setupList(keywordSetup.core_terms || [], "setup-chip setup-chip-primary")}</div></div>
                <div class="setup-term-group"><label>Feature terms</label><div>${setupList(keywordSetup.feature_terms || [])}</div></div>
                <div class="setup-term-group"><label>Style terms</label><div>${setupList(keywordSetup.style_terms || [])}</div></div>
                <div class="setup-term-group"><label>Visual terms</label><div>${setupList(keywordSetup.visual_terms || [])}</div></div>
            `)}

            ${renderSetupSection("Competitors", "group", `
                <div class="setup-term-group"><label>Blocked competitor brands</label><div>${setupList(competitorSetup.blocked_brands || [], "setup-chip setup-chip-danger")}</div></div>
                <div class="setup-competitor-list">
                    ${competitors.length ? competitors.map(comp => `
                        <div class="setup-competitor-item">
                            <strong>${escapeHtml(comp.title || comp.package_id || "Competitor")}</strong>
                            <span>${escapeHtml(comp.package_id || "")}</span>
                            <p>${escapeHtml(comp.short_description || comp.desc200 || "")}</p>
                        </div>
                    `).join("") : '<span class="setup-muted">No competitor apps configured</span>'}
                </div>
            `)}

            ${renderSetupSection("Drop & Risk Rules", "policy", `
                <div class="setup-policy-list">
                    ${(riskSetup.risk_policy || []).map(item => `
                        <div class="setup-policy-row">
                            <span>${escapeHtml(item.name)}</span>
                            <span class="setup-badge ${actionClass(item.action)}">${escapeHtml(item.action)}</span>
                        </div>
                    `).join("")}
                </div>
                <div class="setup-term-group"><label>Noise</label><div>${setupList(riskGroups.noise_terms || [])}</div></div>
                <div class="setup-term-group"><label>Irrelevant intent</label><div>${setupList(riskGroups.irrelevant_intent_terms || [], "setup-chip setup-chip-danger")}</div></div>
                <div class="setup-term-group"><label>Risky platform/IP</label><div>${setupList([...(riskGroups.risky_platform_terms || []), ...(riskGroups.risky_ip_terms || [])], "setup-chip setup-chip-warning")}</div></div>
            `)}

            ${renderSetupSection("Warnings", "warning", `
                <div class="setup-warning-list">
                    ${(warnings.length ? warnings : ["No setup warnings"]).map(warning => `
                        <div class="setup-warning-item">
                            <span class="material-icons-outlined">priority_high</span>
                            <span>${escapeHtml(warning)}</span>
                        </div>
                    `).join("")}
                </div>
            `)}
        </div>
    `;
}
