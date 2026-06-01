const TableState = {
    data: [],
    filteredData: [],
    sortBy: "volume_b",
    sortDesc: true,
    currentPage: 1,
    pageSize: 20,
    initialized: false
};

function renderKeywordsTab(data) {
    TableState.data = data;
    TableState.currentPage = 1;
    
    if (!TableState.initialized) {
        initTableListeners();
        TableState.initialized = true;
    }
    
    applyFiltersAndSort();
}

function initTableListeners() {
    // Search input
    document.getElementById("kw-search").addEventListener("input", () => {
        TableState.currentPage = 1;
        applyFiltersAndSort();
    });

    // Brand/Generic Filter
    document.getElementById("kw-filter-brand").addEventListener("change", () => {
        TableState.currentPage = 1;
        applyFiltersAndSort();
    });

    // Status Filter
    document.getElementById("kw-filter-status").addEventListener("change", () => {
        TableState.currentPage = 1;
        applyFiltersAndSort();
    });

    // Page size dropdown
    document.getElementById("select-page-size").addEventListener("change", (e) => {
        TableState.pageSize = parseInt(e.target.value, 10);
        TableState.currentPage = 1;
        renderTableRows();
    });

    // Pagination buttons
    document.getElementById("pag-prev").addEventListener("click", () => {
        if (TableState.currentPage > 1) {
            TableState.currentPage--;
            renderTableRows();
        }
    });

    document.getElementById("pag-next").addEventListener("click", () => {
        const totalPages = Math.ceil(TableState.filteredData.length / TableState.pageSize);
        if (TableState.currentPage < totalPages) {
            TableState.currentPage++;
            renderTableRows();
        }
    });

    // Sortable headers
    const headers = document.querySelectorAll("#keywords-table th[data-sort]");
    headers.forEach(header => {
        header.addEventListener("click", () => {
            const field = header.getAttribute("data-sort");
            
            if (TableState.sortBy === field) {
                TableState.sortDesc = !TableState.sortDesc;
            } else {
                TableState.sortBy = field;
                TableState.sortDesc = true; // default desc for numeric
                if (field === "keyword" || field === "status") {
                    TableState.sortDesc = false; // default asc for string
                }
            }
            
            // Update UI headers classes
            headers.forEach(h => {
                h.classList.remove("sort-asc", "sort-desc");
            });
            header.classList.add(TableState.sortDesc ? "sort-desc" : "sort-asc");
            
            applyFiltersAndSort();
        });
    });
}

function applyFiltersAndSort() {
    const searchVal = document.getElementById("kw-search").value.toLowerCase().trim();
    const brandFilter = document.getElementById("kw-filter-brand").value;
    const statusFilter = document.getElementById("kw-filter-status").value;
    
    // 1. Apply Filtering
    TableState.filteredData = TableState.data.filter(row => {
        // Search text
        if (searchVal && !row.keyword.toLowerCase().includes(searchVal)) {
            return false;
        }
        
        // Brand filter
        if (brandFilter === "brand" && !row.brand) return false;
        if (brandFilter === "generic" && row.brand) return false;
        
        // Status filter
        if (statusFilter === "new" && row.status !== "New") return false;
        if (statusFilter === "lost" && row.status !== "Lost") return false;
        if (statusFilter === "improved" && row.status !== "↑") return false;
        if (statusFilter === "declined" && row.status !== "↓") return false;
        if (statusFilter === "ranked" && (row.rank_b === 0 || row.rank_b > 100)) return false;
        if (statusFilter === "unranked" && row.rank_b !== 0) return false;
        
        return true;
    });
    
    // 2. Apply Sorting
    const field = TableState.sortBy;
    const desc = TableState.sortDesc;
    
    TableState.filteredData.sort((a, b) => {
        let valA = a[field];
        let valB = b[field];
        
        // Custom handling for rank comparisons
        // In rank comparisons, "Unranked" (0) should be treated as infinity
        if (field === "rank_a" || field === "rank_b") {
            const numA = valA === 0 ? 999999 : valA;
            const numB = valB === 0 ? 999999 : valB;
            return desc ? numB - numA : numA - numB;
        }
        
        // Standard comparison
        if (typeof valA === "string") {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }
        
        if (valA < valB) return desc ? 1 : -1;
        if (valA > valB) return desc ? -1 : 1;
        return 0;
    });
    
    renderTableRows();
}

function renderTableRows() {
    const tbody = document.querySelector("#keywords-table tbody");
    tbody.innerHTML = "";
    
    const totalRows = TableState.filteredData.length;
    document.getElementById("pag-total").textContent = totalRows;
    
    if (totalRows === 0) {
        tbody.innerHTML = '<tr><td colspan="12" style="text-align:center;color:var(--text-secondary);padding:32px;">No keywords match the filters.</td></tr>';
        document.getElementById("pag-start").textContent = "0";
        document.getElementById("pag-end").textContent = "0";
        document.getElementById("pag-prev").disabled = true;
        document.getElementById("pag-next").disabled = true;
        return;
    }
    
    const startIndex = (TableState.currentPage - 1) * TableState.pageSize;
    const endIndex = Math.min(startIndex + TableState.pageSize, totalRows);
    
    document.getElementById("pag-start").textContent = startIndex + 1;
    document.getElementById("pag-end").textContent = endIndex;
    
    // Disable/Enable pagination buttons
    document.getElementById("pag-prev").disabled = TableState.currentPage === 1;
    document.getElementById("pag-next").disabled = endIndex >= totalRows;
    
    const pageRows = TableState.filteredData.slice(startIndex, endIndex);
    
    pageRows.forEach(row => {
        const tr = document.createElement("tr");
        
        // Keyword Cell
        const tdKw = document.createElement("td");
        tdKw.textContent = row.keyword;
        tdKw.style.fontWeight = "500";
        tr.appendChild(tdKw);
        
        // Brand Cell
        const tdBrand = document.createElement("td");
        tdBrand.style.textAlign = "center";
        const badgeBrand = document.createElement("span");
        badgeBrand.className = row.brand ? "badge badge-brand" : "badge badge-generic";
        badgeBrand.textContent = row.brand ? "Brand" : "Generic";
        tdBrand.appendChild(badgeBrand);
        tr.appendChild(tdBrand);
        
        // Volume A Cell
        const tdVolA = document.createElement("td");
        tdVolA.style.textAlign = "right";
        tdVolA.textContent = row.volume_a > 0 ? row.volume_a.toLocaleString() : "—";
        tr.appendChild(tdVolA);
        
        // Volume B Cell
        const tdVolB = document.createElement("td");
        tdVolB.style.textAlign = "right";
        tdVolB.textContent = row.volume_b > 0 ? row.volume_b.toLocaleString() : "—";
        tr.appendChild(tdVolB);
        
        // Volume Delta Cell
        const tdVolDelta = document.createElement("td");
        tdVolDelta.style.textAlign = "right";
        const diffVol = row.diff_volume;
        if (diffVol > 0) {
            tdVolDelta.textContent = `+${diffVol.toLocaleString()}`;
            tdVolDelta.className = "text-success cell-success";
        } else if (diffVol < 0) {
            tdVolDelta.textContent = diffVol.toLocaleString();
            tdVolDelta.className = "text-danger cell-danger";
        } else {
            tdVolDelta.textContent = "—";
            tdVolDelta.className = "text-secondary";
        }
        tr.appendChild(tdVolDelta);
        
        // Difficulty A Cell
        const tdDifA = document.createElement("td");
        tdDifA.style.textAlign = "right";
        tdDifA.textContent = row.difficulty_a || "—";
        tr.appendChild(tdDifA);
        
        // Difficulty B Cell
        const tdDifB = document.createElement("td");
        tdDifB.style.textAlign = "right";
        tdDifB.textContent = row.difficulty_b || "—";
        tr.appendChild(tdDifB);
        
        // Difficulty Delta Cell
        const tdDifDelta = document.createElement("td");
        tdDifDelta.style.textAlign = "right";
        const diffDiff = row.diff_difficulty;
        if (diffDiff > 0) {
            tdDifDelta.textContent = `+${diffDiff}`;
            tdDifDelta.className = "text-danger"; // higher difficulty is usually red
        } else if (diffDiff < 0) {
            tdDifDelta.textContent = diffDiff;
            tdDifDelta.className = "text-success"; // lower difficulty is green
        } else {
            tdDifDelta.textContent = "—";
            tdDifDelta.className = "text-secondary";
        }
        tr.appendChild(tdDifDelta);
        
        // Rank A Cell
        const tdRankA = document.createElement("td");
        tdRankA.style.textAlign = "center";
        tdRankA.textContent = row.rank_a > 0 ? row.rank_a : "Unranked";
        tr.appendChild(tdRankA);
        
        // Rank B Cell
        const tdRankB = document.createElement("td");
        tdRankB.style.textAlign = "center";
        tdRankB.textContent = row.rank_b > 0 ? row.rank_b : "Unranked";
        tr.appendChild(tdRankB);
        
        // Rank Delta Cell
        const tdRankDelta = document.createElement("td");
        tdRankDelta.style.textAlign = "center";
        const diffRank = row.diff_rank;
        if (diffRank < 0) { // Rank improved
            tdRankDelta.textContent = `↑ ${Math.abs(diffRank)}`;
            tdRankDelta.className = "text-success cell-success";
        } else if (diffRank > 0) { // Rank dropped
            tdRankDelta.textContent = `↓ ${diffRank}`;
            tdRankDelta.className = "text-danger cell-danger";
        } else {
            tdRankDelta.textContent = "—";
            tdRankDelta.className = "text-secondary";
        }
        tr.appendChild(tdRankDelta);
        
        // Status Cell
        const tdStatus = document.createElement("td");
        tdStatus.style.textAlign = "center";
        const badgeStatus = document.createElement("span");
        if (row.status === "New") {
            badgeStatus.className = "badge badge-new";
            badgeStatus.textContent = "New";
        } else if (row.status === "Lost") {
            badgeStatus.className = "badge badge-lost";
            badgeStatus.textContent = "Lost";
        } else if (row.status === "↑") {
            badgeStatus.className = "text-success";
            badgeStatus.style.fontWeight = "bold";
            badgeStatus.textContent = "↑";
        } else if (row.status === "↓") {
            badgeStatus.className = "text-danger";
            badgeStatus.style.fontWeight = "bold";
            badgeStatus.textContent = "↓";
        } else {
            badgeStatus.className = "text-secondary";
            badgeStatus.textContent = "—";
        }
        tdStatus.appendChild(badgeStatus);
        tr.appendChild(tdStatus);
        
        // Click row to show in Trend Tab!
        tr.style.cursor = "pointer";
        tr.addEventListener("click", (e) => {
            // Avoid triggering when clicking elements inside cell
            switchTab("trends");
            // Highlight this keyword in trend tab
            setTimeout(() => {
                selectKeywordInTrend(row.keyword);
            }, 100);
        });
        
        tbody.appendChild(tr);
    });
}
