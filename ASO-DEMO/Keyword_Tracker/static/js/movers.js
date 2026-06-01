function renderMoversTab(moversData) {
    if (!moversData) return;
    
    populateGainersList(moversData.gainers);
    populateLosersList(moversData.losers);
    populateNewList(moversData.new);
    populateLostList(moversData.lost);
}

function populateGainersList(gainers) {
    const tbody = document.getElementById("movers-gainers-list");
    tbody.innerHTML = "";
    
    if (!gainers || gainers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary);padding:16px;">No gainers in this period.</td></tr>';
        return;
    }
    
    gainers.forEach(row => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.addEventListener("click", () => {
            switchTab("trends");
            setTimeout(() => {
                selectKeywordInTrend(row.keyword);
            }, 100);
        });
        
        const tdKw = document.createElement("td");
        tdKw.textContent = row.keyword;
        tdKw.style.fontWeight = "500";
        tr.appendChild(tdKw);
        
        const tdOld = document.createElement("td");
        tdOld.style.textAlign = "center";
        tdOld.textContent = row.rank_a > 0 ? row.rank_a : "Unranked";
        tr.appendChild(tdOld);
        
        const tdNew = document.createElement("td");
        tdNew.style.textAlign = "center";
        tdNew.textContent = row.rank_b > 0 ? row.rank_b : "Unranked";
        tr.appendChild(tdNew);
        
        const tdChange = document.createElement("td");
        tdChange.style.textAlign = "center";
        tdChange.className = "text-success mover-diff-col";
        // Calculate diff: if rank_a was unranked (0), show entry. Else show numeric difference.
        if (row.rank_a === 0) {
            tdChange.textContent = "New Rank";
        } else {
            const diff = row.rank_a - row.rank_b; // improvement is positive for display
            tdChange.textContent = `↑ ${diff}`;
        }
        tr.appendChild(tdChange);
        
        tbody.appendChild(tr);
    });
}

function populateLosersList(losers) {
    const tbody = document.getElementById("movers-losers-list");
    tbody.innerHTML = "";
    
    if (!losers || losers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary);padding:16px;">No losers in this period.</td></tr>';
        return;
    }
    
    losers.forEach(row => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.addEventListener("click", () => {
            switchTab("trends");
            setTimeout(() => {
                selectKeywordInTrend(row.keyword);
            }, 100);
        });
        
        const tdKw = document.createElement("td");
        tdKw.textContent = row.keyword;
        tdKw.style.fontWeight = "500";
        tr.appendChild(tdKw);
        
        const tdOld = document.createElement("td");
        tdOld.style.textAlign = "center";
        tdOld.textContent = row.rank_a > 0 ? row.rank_a : "Unranked";
        tr.appendChild(tdOld);
        
        const tdNew = document.createElement("td");
        tdNew.style.textAlign = "center";
        tdNew.textContent = row.rank_b > 0 ? row.rank_b : "Unranked";
        tr.appendChild(tdNew);
        
        const tdChange = document.createElement("td");
        tdChange.style.textAlign = "center";
        tdChange.className = "text-danger mover-diff-col";
        if (row.rank_b === 0) {
            tdChange.textContent = "Out";
        } else {
            const diff = row.rank_b - row.rank_a; // decline is positive for drop count display
            tdChange.textContent = `↓ ${diff}`;
        }
        tr.appendChild(tdChange);
        
        tbody.appendChild(tr);
    });
}

function populateNewList(newList) {
    const tbody = document.getElementById("movers-new-list");
    tbody.innerHTML = "";
    
    if (!newList || newList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary);padding:16px;">No new keywords.</td></tr>';
        return;
    }
    
    newList.forEach(row => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.addEventListener("click", () => {
            switchTab("trends");
            setTimeout(() => {
                selectKeywordInTrend(row.keyword);
            }, 100);
        });
        
        const tdKw = document.createElement("td");
        tdKw.textContent = row.keyword;
        tdKw.style.fontWeight = "500";
        tr.appendChild(tdKw);
        
        const tdVol = document.createElement("td");
        tdVol.style.textAlign = "center";
        tdVol.textContent = row.volume_b > 0 ? row.volume_b.toLocaleString() : "—";
        tr.appendChild(tdVol);
        
        const tdDif = document.createElement("td");
        tdDif.style.textAlign = "center";
        tdDif.textContent = row.difficulty_b || "—";
        tr.appendChild(tdDif);
        
        const tdRank = document.createElement("td");
        tdRank.style.textAlign = "center";
        tdRank.textContent = row.rank_b > 0 ? row.rank_b : "Unranked";
        tr.appendChild(tdRank);
        
        tbody.appendChild(tr);
    });
}

function populateLostList(lostList) {
    const tbody = document.getElementById("movers-lost-list");
    tbody.innerHTML = "";
    
    if (!lostList || lostList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;color:var(--text-secondary);padding:16px;">No lost keywords.</td></tr>';
        return;
    }
    
    lostList.forEach(row => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.addEventListener("click", () => {
            switchTab("trends");
            setTimeout(() => {
                selectKeywordInTrend(row.keyword);
            }, 100);
        });
        
        const tdKw = document.createElement("td");
        tdKw.textContent = row.keyword;
        tdKw.style.fontWeight = "500";
        tr.appendChild(tdKw);
        
        const tdVol = document.createElement("td");
        tdVol.style.textAlign = "center";
        tdVol.textContent = row.volume_a > 0 ? row.volume_a.toLocaleString() : "—";
        tr.appendChild(tdVol);
        
        const tdRank = document.createElement("td");
        tdRank.style.textAlign = "center";
        tdRank.textContent = row.rank_a > 0 ? row.rank_a : "Unranked";
        tr.appendChild(tdRank);
        
        tbody.appendChild(tr);
    });
}
