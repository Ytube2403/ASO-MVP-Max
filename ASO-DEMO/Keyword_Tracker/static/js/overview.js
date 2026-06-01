// Global references to ECharts instances to allow resizing
let powerScoreChart = null;
let rankDistChart = null;

function renderOverviewTab(overviewData, monthA, monthB) {
    if (!overviewData || overviewData.length === 0) return;

    // Find Month B and Month A datasets
    const dataB = overviewData.find(d => d.month === monthB) || overviewData[overviewData.length - 1];
    
    // Default Month A: if not selected, try to take the index before Month B
    let dataA = null;
    if (monthA) {
        dataA = overviewData.find(d => d.month === monthA);
    } else {
        const idxB = overviewData.findIndex(d => d.month === monthB);
        if (idxB > 0) {
            dataA = overviewData[idxB - 1];
        }
    }

    // 1. Calculate and populate KPI values
    const scoreB = dataB ? dataB.aso_power_score : 0;
    const scoreA = dataA ? dataA.aso_power_score : 0;
    const scoreDelta = scoreB - scoreA;
    
    document.getElementById("overview-power-score").textContent = scoreB.toLocaleString();
    formatDelta("overview-power-score-delta", scoreDelta, true);

    const totalB = dataB ? dataB.tiers.total_keywords : 0;
    const totalA = dataA ? dataA.tiers.total_keywords : 0;
    const totalDelta = totalB - totalA;
    
    document.getElementById("overview-total-keywords").textContent = totalB.toLocaleString();
    formatDelta("overview-total-keywords-delta", totalDelta, false);

    // Ranked = total - unranked
    const unrankedB = dataB ? dataB.tiers.unranked : 0;
    const rankedB = totalB - unrankedB;
    const pctRankedB = totalB > 0 ? ((rankedB / totalB) * 100).toFixed(1) : "0.0";
    
    const unrankedA = dataA ? dataA.tiers.unranked : 0;
    const rankedA = totalA - unrankedA;
    const rankedDelta = rankedB - rankedA;
    
    document.getElementById("overview-ranked-keywords").textContent = `${rankedB.toLocaleString()} (${pctRankedB}%)`;
    formatDelta("overview-ranked-keywords-delta", rankedDelta, false);

    // Rank Movers from AppState.keywordsData
    let upCount = 0;
    let downCount = 0;
    
    if (AppState.keywordsData) {
        AppState.keywordsData.forEach(row => {
            if (row.status === "↑") {
                upCount++;
            } else if (row.status === "↓") {
                downCount++;
            }
        });
    }
    
    document.getElementById("overview-rank-up").textContent = upCount.toLocaleString();
    document.getElementById("overview-rank-down").textContent = downCount.toLocaleString();

    // 2. Render Charts
    initPowerScoreChart(overviewData);
    initRankDistChart(overviewData);
}

function formatDelta(elementId, delta, showPlus = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    if (delta > 0) {
        el.textContent = `${showPlus ? '+' : ''}${delta.toLocaleString()}`;
        el.className = "kpi-delta success";
    } else if (delta < 0) {
        el.textContent = `${delta.toLocaleString()}`;
        el.className = "kpi-delta danger";
    } else {
        el.textContent = "—";
        el.className = "kpi-delta";
    }
}

function initPowerScoreChart(overviewData) {
    const chartDom = document.getElementById("chart-power-score");
    if (!chartDom) return;
    
    if (powerScoreChart) {
        powerScoreChart.dispose();
    }
    
    powerScoreChart = echarts.init(chartDom);
    
    const months = overviewData.map(d => window.formatMonthString(d.month));
    const scores = overviewData.map(d => d.aso_power_score);
    
    const option = {
        tooltip: {
            trigger: "axis",
            backgroundColor: "#202124",
            textStyle: { color: "#ffffff", fontFamily: "Outfit" },
            formatter: function (params) {
                const p = params[0];
                return `<div style="font-weight:600;margin-bottom:4px;">${p.name}</div>
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background-color:#1a73e8;"></span>
                            <span>Score: <b>${p.value.toLocaleString()}</b></span>
                        </div>`;
            }
        },
        grid: {
            left: "3%",
            right: "4%",
            bottom: "3%",
            top: "8%",
            containLabel: true
        },
        xAxis: {
            type: "category",
            boundaryGap: false,
            data: months,
            axisLine: { lineStyle: { color: "#dadce0" } },
            axisLabel: { color: "#5f6368", fontFamily: "Outfit", fontSize: 11 }
        },
        yAxis: {
            type: "value",
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: "#f1f3f4" } },
            axisLabel: { color: "#5f6368", fontFamily: "Outfit", fontSize: 11 }
        },
        series: [
            {
                name: "ASO Power Score",
                type: "line",
                smooth: true,
                symbol: "circle",
                symbolSize: 8,
                showSymbol: true,
                data: scores,
                itemStyle: { color: "#1a73e8" },
                lineStyle: { width: 3, color: "#1a73e8" },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: "rgba(26, 115, 232, 0.3)" },
                        { offset: 1, color: "rgba(26, 115, 232, 0.01)" }
                    ])
                }
            }
        ]
    };
    
    powerScoreChart.setOption(option);
}

function initRankDistChart(overviewData) {
    const chartDom = document.getElementById("chart-rank-distribution");
    if (!chartDom) return;
    
    if (rankDistChart) {
        rankDistChart.dispose();
    }
    
    rankDistChart = echarts.init(chartDom);
    
    const months = overviewData.map(d => window.formatMonthString(d.month));
    const top1 = overviewData.map(d => d.tiers.top_1);
    const top23 = overviewData.map(d => d.tiers.top_2_3);
    const top410 = overviewData.map(d => d.tiers.top_4_10);
    const top1130 = overviewData.map(d => d.tiers.top_11_30);
    const top31100 = overviewData.map(d => d.tiers.top_31_100);
    const unranked = overviewData.map(d => d.tiers.unranked);
    
    const option = {
        tooltip: {
            trigger: "axis",
            axisPointer: { type: "shadow" },
            backgroundColor: "#202124",
            textStyle: { color: "#ffffff", fontFamily: "Outfit" }
        },
        legend: {
            data: ["Top 1", "Top 2-3", "Top 4-10", "Top 11-30", "Top 31-100", "Unranked"],
            textStyle: { color: "#5f6368", fontFamily: "Outfit", fontSize: 11 },
            top: "0%"
        },
        grid: {
            left: "3%",
            right: "4%",
            bottom: "3%",
            top: "15%",
            containLabel: true
        },
        xAxis: {
            type: "category",
            data: months,
            axisLine: { lineStyle: { color: "#dadce0" } },
            axisLabel: { color: "#5f6368", fontFamily: "Outfit", fontSize: 11 }
        },
        yAxis: {
            type: "value",
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { lineStyle: { color: "#f1f3f4" } },
            axisLabel: { color: "#5f6368", fontFamily: "Outfit", fontSize: 11 }
        },
        series: [
            {
                name: "Top 1",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: top1,
                itemStyle: { color: "#fbbc05" } // Gold
            },
            {
                name: "Top 2-3",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: top23,
                itemStyle: { color: "#ff8f00" } // Dark Orange/Silver accent
            },
            {
                name: "Top 4-10",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: top410,
                itemStyle: { color: "#ff6d00" } // Bronze/Orange
            },
            {
                name: "Top 11-30",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: top1130,
                itemStyle: { color: "#1a73e8" } // Blue
            },
            {
                name: "Top 31-100",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: top31100,
                itemStyle: { color: "#78909c" } // Gray-Blue
            },
            {
                name: "Unranked",
                type: "bar",
                stack: "total",
                emphasis: { focus: "series" },
                data: unranked,
                itemStyle: { color: "#cfd8dc" } // Light Gray
            }
        ]
    };
    
    rankDistChart.setOption(option);
}

// Window resize handler to make charts fully responsive
window.addEventListener("resize", () => {
    if (powerScoreChart) powerScoreChart.resize();
    if (rankDistChart) rankDistChart.resize();
});
