let trendChart = null;
let trendKeywordsList = [];

function renderTrendsTab(keywordsData) {
    if (!keywordsData || keywordsData.length === 0) {
        document.getElementById("trend-selected-keyword").textContent = "No keywords available";
        return;
    }
    
    // Cache the keywords data (sorted by Volume B desc)
    trendKeywordsList = keywordsData.map(k => ({
        keyword: k.keyword,
        brand: k.brand
    }));
    
    // Setup listeners if not already
    const searchInput = document.getElementById("trend-kw-search");
    searchInput.replaceWith(searchInput.cloneNode(true)); // clear listeners
    document.getElementById("trend-kw-search").addEventListener("input", filterTrendKeywordsList);
    
    // Initial render of the keyword list in sidebar
    populateTrendKeywordsList("");
    
    // Select first keyword by default on initial render
    const firstActiveLi = document.querySelector("#trend-kw-list li");
    if (firstActiveLi) {
        const kw = firstActiveLi.getAttribute("data-kw");
        selectKeywordInTrend(kw);
    }
}

function populateTrendKeywordsList(filterText) {
    const listUl = document.getElementById("trend-kw-list");
    listUl.innerHTML = "";
    
    const filtered = trendKeywordsList.filter(item => 
        item.keyword.toLowerCase().includes(filterText.toLowerCase())
    );
    
    if (filtered.length === 0) {
        listUl.innerHTML = '<li style="text-align:center;color:var(--text-secondary);cursor:default;">No match</li>';
        return;
    }
    
    filtered.forEach((item, index) => {
        const li = document.createElement("li");
        li.textContent = item.keyword;
        li.setAttribute("data-kw", item.keyword);
        
        // Add visual indicator if brand
        if (item.brand) {
            const brandSpan = document.createElement("span");
            brandSpan.style.float = "right";
            brandSpan.style.fontSize = "10px";
            brandSpan.style.color = "var(--primary)";
            brandSpan.style.border = "1px solid var(--primary)";
            brandSpan.style.borderRadius = "3px";
            brandSpan.style.padding = "0 3px";
            brandSpan.style.marginTop = "2px";
            brandSpan.textContent = "B";
            li.appendChild(brandSpan);
        }
        
        li.addEventListener("click", () => {
            document.querySelectorAll("#trend-kw-list li").forEach(el => el.classList.remove("active"));
            li.classList.add("active");
            loadKeywordTrend(item.keyword, item.brand);
        });
        
        listUl.appendChild(li);
    });
}

function filterTrendKeywordsList(e) {
    populateTrendKeywordsList(e.target.value);
}

// Global function to select a specific keyword (called from Keyword Table row click)
function selectKeywordInTrend(keyword) {
    // 1. Ensure keyword list is populated and unfiltered
    document.getElementById("trend-kw-search").value = "";
    populateTrendKeywordsList("");
    
    // 2. Find the li element
    const items = document.querySelectorAll("#trend-kw-list li");
    let targetLi = null;
    items.forEach(li => {
        if (li.getAttribute("data-kw") === keyword) {
            targetLi = li;
        }
    });
    
    if (targetLi) {
        // Remove active from others, make this active
        items.forEach(el => el.classList.remove("active"));
        targetLi.classList.add("active");
        
        // Scroll into view within parent UL
        targetLi.scrollIntoView({ block: "nearest", behavior: "smooth" });
        
        // Load trend
        const isBrand = trendKeywordsList.find(k => k.keyword === keyword)?.brand || false;
        loadKeywordTrend(keyword, isBrand);
    } else {
        // Fallback: If not found in the list, fetch and load manually
        loadKeywordTrend(keyword, false);
    }
}
window.selectKeywordInTrend = selectKeywordInTrend; // expose to window

async function loadKeywordTrend(keyword, isBrand) {
    // Update Header
    document.getElementById("trend-selected-keyword").textContent = keyword;
    const badge = document.getElementById("trend-keyword-brand");
    if (isBrand) {
        badge.classList.remove("hidden");
        badge.className = "badge badge-brand";
        badge.textContent = "Brand";
    } else {
        badge.classList.remove("hidden");
        badge.className = "badge badge-generic";
        badge.textContent = "Generic";
    }
    
    try {
        const response = await fetch(`/api/trend/${AppState.selectedApp}/${AppState.selectedLocale}/${encodeURIComponent(keyword)}`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            const data = result.data;
            const latest = data[data.length - 1];
            
            // Populate Metrics summary
            document.getElementById("trend-metrics-summary").classList.remove("hidden");
            document.getElementById("trend-val-volume").textContent = latest.volume ? latest.volume.toLocaleString() : "—";
            document.getElementById("trend-val-difficulty").textContent = latest.difficulty || "—";
            document.getElementById("trend-val-rank").textContent = latest.rank > 0 ? latest.rank : "Unranked";
            document.getElementById("trend-val-kei").textContent = latest.kei || "—";
            
            renderTrendChart(data);
        } else {
            document.getElementById("trend-metrics-summary").classList.add("hidden");
            if (trendChart) trendChart.clear();
        }
    } catch (e) {
        console.error("Error fetching trend data for keyword: " + keyword, e);
    }
}

function renderTrendChart(trendData) {
    const chartDom = document.getElementById("chart-keyword-trend");
    if (!chartDom) return;
    
    if (trendChart) {
        trendChart.dispose();
    }
    
    trendChart = echarts.init(chartDom);
    
    const months = trendData.map(d => window.formatMonthString(d.month));
    const volumes = trendData.map(d => d.volume || 0);
    const ranks = trendData.map(d => d.rank > 0 ? d.rank : null); // null doesn't plot or shows gap
    
    const option = {
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "cross" },
            backgroundColor: "#202124",
            textStyle: { color: "#ffffff", fontFamily: "Outfit" },
            formatter: function (params) {
                let html = `<div style="font-weight:600;margin-bottom:6px;">${params[0].name}</div>`;
                params.forEach(p => {
                    let val = p.value;
                    if (p.seriesName === "Rank") {
                        val = val === null || val === undefined ? "Unranked" : val;
                    } else {
                        val = val ? val.toLocaleString() : 0;
                    }
                    html += `<div style="display:flex;align-items:center;justify-content:space-between;gap:16px;">
                                <span style="display:inline-flex;align-items:center;gap:6px;">
                                    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:${p.color};"></span>
                                    <span>${p.seriesName}:</span>
                                </span>
                                <b>${val}</b>
                             </div>`;
                });
                return html;
            }
        },
        legend: {
            data: ["Volume", "Rank"],
            textStyle: { color: "#5f6368", fontFamily: "Outfit" }
        },
        grid: {
            left: "3%",
            right: "4%",
            bottom: "3%",
            top: "12%",
            containLabel: true
        },
        xAxis: {
            type: "category",
            data: months,
            axisLine: { lineStyle: { color: "#dadce0" } },
            axisLabel: { color: "#5f6368", fontFamily: "Outfit" }
        },
        yAxis: [
            {
                type: "value",
                name: "Volume",
                position: "left",
                axisLine: { show: true, lineStyle: { color: "#1a73e8" } },
                axisLabel: { color: "#1a73e8", fontFamily: "Outfit" },
                splitLine: { show: true, lineStyle: { color: "#f1f3f4" } }
            },
            {
                type: "value",
                name: "Rank",
                position: "right",
                inverse: true, // Rank 1 is top, rank 100 is bottom!
                min: 1,
                // Automatically find reasonable max rank to scale (e.g. max rank or 100)
                max: function (value) {
                    return Math.max(100, value.max + 10);
                },
                axisLine: { show: true, lineStyle: { color: "#ea4335" } },
                axisLabel: { color: "#ea4335", fontFamily: "Outfit" },
                splitLine: { show: false }
            }
        ],
        series: [
            {
                name: "Volume",
                type: "line",
                smooth: true,
                yAxisIndex: 0,
                data: volumes,
                itemStyle: { color: "#1a73e8" },
                lineStyle: { width: 3 }
            },
            {
                name: "Rank",
                type: "line",
                smooth: true,
                connectNulls: false, // Don't connect points over unranked months
                yAxisIndex: 1,
                data: ranks,
                itemStyle: { color: "#ea4335" },
                lineStyle: { width: 3, type: "dashed" },
                symbol: "circle",
                symbolSize: 8
            }
        ]
    };
    
    trendChart.setOption(option);
}

window.addEventListener("resize", () => {
    if (trendChart) trendChart.resize();
});
