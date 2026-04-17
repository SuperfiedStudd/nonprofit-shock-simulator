from __future__ import annotations

from .logic import risk_bucket_color

try:
    import plotly.graph_objects as _go
    import plotly.io as _pio

    _SL_PRIMARY = "#000613"
    _SL_PRIMARY_CONTAINER = "#001f3f"
    _SL_ON_SURFACE = "#1a1c1b"
    _SL_ON_SURFACE_VARIANT = "#43474e"
    _SL_OUTLINE = "#74777f"
    _SL_OUTLINE_VARIANT = "#c4c6cf"
    _SL_SURFACE = "#faf9f7"
    _SL_SURFACE_LOWEST = "#ffffff"
    _SL_SURFACE_LOW = "#f4f3f1"
    _SL_TERTIARY_DIM = "#fdb69a"
    _SL_SECONDARY = "#565f6e"
    _SL_SURFACE_TINT = "#476083"
    _SL_HAIRLINE = "rgba(196, 198, 207, 0.35)"

    _sl_template = _go.layout.Template()
    _sl_template.layout = _go.Layout(
        font=dict(family='"Manrope", "Helvetica Neue", Arial, sans-serif', color=_SL_ON_SURFACE, size=13),
        title=dict(
            font=dict(family='"Newsreader", Georgia, serif', size=20, color=_SL_PRIMARY, weight=400),
            x=0.0, xanchor="left", pad=dict(b=14),
        ),
        paper_bgcolor=_SL_SURFACE_LOWEST,
        plot_bgcolor=_SL_SURFACE_LOWEST,
        colorway=[_SL_PRIMARY, _SL_TERTIARY_DIM, _SL_SURFACE_TINT, _SL_SECONDARY, _SL_PRIMARY_CONTAINER, _SL_OUTLINE, "#6f88ad", "#b5785f"],
        xaxis=dict(
            gridcolor=_SL_HAIRLINE, gridwidth=1, zeroline=False,
            linecolor=_SL_HAIRLINE, linewidth=1,
            tickcolor=_SL_HAIRLINE,
            tickfont=dict(family='"Manrope", sans-serif', size=11, color=_SL_OUTLINE),
            title=dict(font=dict(family='"Manrope", sans-serif', size=11, color=_SL_ON_SURFACE_VARIANT)),
            ticks="outside", ticklen=4,
        ),
        yaxis=dict(
            gridcolor=_SL_HAIRLINE, gridwidth=1, zeroline=False,
            linecolor=_SL_HAIRLINE, linewidth=1,
            tickcolor=_SL_HAIRLINE,
            tickfont=dict(family='"Manrope", sans-serif', size=11, color=_SL_OUTLINE),
            title=dict(font=dict(family='"Manrope", sans-serif', size=11, color=_SL_ON_SURFACE_VARIANT)),
            ticks="outside", ticklen=4,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor=_SL_HAIRLINE, borderwidth=0,
            font=dict(family='"Manrope", sans-serif', size=12, color=_SL_ON_SURFACE_VARIANT),
        ),
        hoverlabel=dict(
            bgcolor=_SL_PRIMARY, bordercolor=_SL_PRIMARY,
            font=dict(family='"Manrope", sans-serif', color="#ffffff", size=12),
        ),
        margin=dict(l=56, r=24, t=44, b=52),
        colorscale=dict(
            sequential=[[0.0, "#e3e2e0"], [0.5, _SL_SURFACE_TINT], [1.0, _SL_PRIMARY]],
            diverging=[[0, _SL_TERTIARY_DIM], [0.5, _SL_SURFACE_LOWEST], [1, _SL_PRIMARY]],
        ),
    )
    _pio.templates["sovereign"] = _sl_template
    _pio.templates.default = "sovereign"
except Exception:
    pass


GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,400;6..72,500;6..72,600;6..72,700&family=Manrope:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL@20..48,100..700,0..1&display=swap');

    :root {
        --sl-background: #faf9f7;
        --sl-primary: #000613;
        --sl-primary-container: #001f3f;
        --sl-on-primary: #ffffff;
        --sl-on-surface: #1a1c1b;
        --sl-on-surface-variant: #43474e;
        --sl-outline: #74777f;
        --sl-outline-variant: #c4c6cf;
        --sl-surface: #faf9f7;
        --sl-surface-lowest: #ffffff;
        --sl-surface-low: #f4f3f1;
        --sl-surface-container: #efeeec;
        --sl-surface-high: #e9e8e6;
        --sl-surface-highest: #e3e2e0;
        --sl-tertiary-dim: #fdb69a;
        --sl-tertiary-container: #391303;
        --sl-surface-tint: #476083;
        --sl-hairline: rgba(196, 198, 207, 0.35);
        --sl-hairline-soft: rgba(196, 198, 207, 0.2);
        --sl-font-display: "Newsreader", Georgia, serif;
        --sl-font-body: "Manrope", "Helvetica Neue", Arial, sans-serif;
        --sl-t-fast: 140ms cubic-bezier(0.2, 0, 0, 1);
        --sl-t: 220ms cubic-bezier(0.34, 1.56, 0.64, 1);
        --sl-radius: 0px;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            transition-duration: 0.001ms !important;
            animation-duration: 0.001ms !important;
        }
    }

    @keyframes sovereign-rise {
        0%   { opacity: 0; transform: translateY(14px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    @keyframes sovereign-fade {
        0%   { opacity: 0; }
        100% { opacity: 1; }
    }

    .mat {
        font-family: "Material Symbols Outlined";
        font-weight: normal; font-style: normal;
        font-size: 18px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: "liga";
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
        font-variation-settings: "FILL" 0, "wght" 300, "GRAD" 0, "opsz" 24;
    }
    .mat.fill { font-variation-settings: "FILL" 1, "wght" 400, "GRAD" 0, "opsz" 24; }
    .mat.sm  { font-size: 14px; }
    .mat.lg  { font-size: 22px; }

    /* ---------- Bento Grid Layout ---------- */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(12, minmax(0, 1fr));
        gap: 1.5rem;
        margin: 0 0 1.8rem 0;
    }
    .bento-grid.tight { gap: 0.9rem; }
    .bento-grid.airy  { gap: 2rem; }

    .bento-span-1  { grid-column: span 1;  }
    .bento-span-2  { grid-column: span 2;  }
    .bento-span-3  { grid-column: span 3;  }
    .bento-span-4  { grid-column: span 4;  }
    .bento-span-5  { grid-column: span 5;  }
    .bento-span-6  { grid-column: span 6;  }
    .bento-span-7  { grid-column: span 7;  }
    .bento-span-8  { grid-column: span 8;  }
    .bento-span-9  { grid-column: span 9;  }
    .bento-span-10 { grid-column: span 10; }
    .bento-span-11 { grid-column: span 11; }
    .bento-span-12 { grid-column: span 12; }
    @media (max-width: 900px) {
        .bento-grid { grid-template-columns: 1fr; }
        .bento-span-1, .bento-span-2, .bento-span-3, .bento-span-4, .bento-span-5,
        .bento-span-6, .bento-span-7, .bento-span-8, .bento-span-9, .bento-span-10,
        .bento-span-11, .bento-span-12 { grid-column: span 1; }
    }

    .bento-card {
        background: var(--sl-surface-lowest);
        border: 0.5px solid var(--sl-hairline-soft);
        border-radius: 0;
        padding: 2rem 2.2rem;
        box-shadow: none;
        transition: transform var(--sl-t), border-color var(--sl-t), background-color var(--sl-t);
        display: flex; flex-direction: column; justify-content: space-between;
        min-height: 220px;
        position: relative;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) both;
    }
    .bento-card.tonal-low     { background: var(--sl-surface-low); border-color: transparent; }
    .bento-card.tonal-high    { background: var(--sl-surface-highest); border-color: transparent; }
    .bento-card.inverse       { background: var(--sl-primary); color: var(--sl-on-primary); border-color: transparent; }
    .bento-card.inverse *     { color: var(--sl-on-primary) !important; }
    .bento-card:hover {
        transform: scale(1.015);
        border-color: var(--sl-hairline);
    }
    .bento-card > .mat {
        position: absolute;
        top: 1.4rem; right: 1.4rem;
        color: var(--sl-primary);
        background: var(--sl-surface-container);
        padding: 0.45rem;
    }
    .bento-card.inverse > .mat {
        background: rgba(255,255,255,0.08);
        color: var(--sl-on-primary);
    }
    .bento-card .bento-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
        margin-bottom: 0.9rem;
    }
    .bento-card.inverse .bento-kicker { color: rgba(255,255,255,0.7); }
    .bento-card .bento-title {
        font-family: var(--sl-font-display);
        font-size: 1.45rem;
        font-weight: 500;
        font-variation-settings: "opsz" 36;
        letter-spacing: -0.02em;
        color: var(--sl-primary);
        margin-bottom: 0.45rem;
    }
    .bento-card.inverse .bento-title { color: var(--sl-on-primary); }
    .bento-card .bento-sub {
        font-family: var(--sl-font-body);
        font-size: 0.88rem;
        line-height: 1.6;
        color: var(--sl-on-surface-variant);
    }
    .bento-card.inverse .bento-sub { color: rgba(255,255,255,0.78); }
    .bento-card .bento-value {
        font-family: var(--sl-font-display);
        font-size: 4.5rem;
        font-weight: 400;
        font-variation-settings: "opsz" 72;
        line-height: 1;
        letter-spacing: -0.04em;
        color: var(--sl-primary);
        margin: 1.4rem 0 0.2rem 0;
    }
    .bento-card.inverse .bento-value { color: var(--sl-on-primary); }
    .bento-card .bento-value .unit {
        font-family: var(--sl-font-body);
        font-size: 1.1rem;
        font-weight: 500;
        color: var(--sl-outline);
        margin-left: 0.4rem;
        letter-spacing: 0;
    }
    .bento-card .bento-delta {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: var(--sl-surface-low);
        padding: 0.35rem 0.7rem;
        font-family: var(--sl-font-body);
        font-size: 0.76rem;
        font-weight: 500;
        color: var(--sl-primary);
        margin-top: 0.9rem;
    }
    .bento-card .bento-delta.warn { color: var(--sl-tertiary-dim); background: rgba(253,182,154,0.1); }
    .bento-card.inverse .bento-delta { background: rgba(255,255,255,0.1); color: var(--sl-on-primary); }
    .bento-card .bento-progress {
        height: 2px; width: 100%;
        background: var(--sl-surface-highest);
        margin: 0.9rem 0 0.4rem 0;
    }
    .bento-card .bento-progress > span {
        display: block; height: 100%;
        background: var(--sl-primary);
    }
    .bento-card.inverse .bento-progress { background: rgba(255,255,255,0.16); }
    .bento-card.inverse .bento-progress > span { background: var(--sl-on-primary); }
    .bento-card .bento-footer {
        display: flex; justify-content: space-between; align-items: center;
        margin-top: 1rem;
        padding-top: 0.9rem;
        border-top: 0.5px solid var(--sl-hairline-soft);
        font-family: var(--sl-font-body);
        font-size: 0.72rem;
        color: var(--sl-outline);
    }

    /* Stagger children for entrance choreography */
    .bento-grid > .bento-card:nth-child(1) { animation-delay: 40ms;  }
    .bento-grid > .bento-card:nth-child(2) { animation-delay: 100ms; }
    .bento-grid > .bento-card:nth-child(3) { animation-delay: 160ms; }
    .bento-grid > .bento-card:nth-child(4) { animation-delay: 220ms; }
    .bento-grid > .bento-card:nth-child(5) { animation-delay: 280ms; }
    .bento-grid > .bento-card:nth-child(6) { animation-delay: 340ms; }
    .bento-grid > .bento-card:nth-child(7) { animation-delay: 400ms; }
    .bento-grid > .bento-card:nth-child(8) { animation-delay: 460ms; }

    /* Action Panel (dark navy strip) */
    .action-panel {
        background: var(--sl-primary);
        color: var(--sl-on-primary);
        border: 0;
        padding: 2.4rem 2.6rem;
        display: flex;
        flex-direction: column;
        gap: 1.3rem;
        justify-content: space-between;
        align-items: flex-start;
        margin: 0 0 1.8rem 0;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) 400ms both;
    }
    @media (min-width: 900px) {
        .action-panel { flex-direction: row; align-items: center; gap: 2rem; }
    }
    .action-panel .panel-copy { max-width: 42rem; }
    .action-panel .panel-title {
        font-family: var(--sl-font-display);
        font-size: 1.55rem;
        font-weight: 500;
        color: var(--sl-on-primary);
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .action-panel .panel-sub {
        font-family: var(--sl-font-body);
        font-size: 0.9rem;
        line-height: 1.65;
        color: rgba(255,255,255,0.78);
    }
    .action-panel .panel-cta {
        display: inline-flex; align-items: center; gap: 0.55rem;
        background: var(--sl-surface-lowest);
        color: var(--sl-primary);
        font-family: var(--sl-font-body);
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        padding: 1rem 1.8rem;
        border: 0;
        cursor: default;
        white-space: nowrap;
        transition: background-color var(--sl-t);
    }
    .action-panel .panel-cta:hover { background: var(--sl-surface-highest); }

    /* ---------- Reference Overview: Executive Header ---------- */
    .exec-header {
        display: flex; flex-direction: column; gap: 1.5rem;
        padding: 0 0 1.6rem 0;
        margin: 0 0 1.5rem 0;
        border-bottom: 0.5px solid var(--sl-hairline);
        animation: sovereign-fade 450ms ease-out both;
    }
    @media (min-width: 900px) {
        .exec-header { flex-direction: row; justify-content: space-between; align-items: flex-end; }
    }
    .exec-header .exec-title {
        font-family: var(--sl-font-display);
        font-size: 3.1rem;
        font-weight: 400;
        font-variation-settings: "opsz" 56;
        line-height: 1.08;
        letter-spacing: -0.035em;
        color: var(--sl-primary);
        margin: 0 0 0.9rem 0;
        max-width: 42rem;
    }
    .exec-header .exec-body {
        font-family: var(--sl-font-body);
        font-size: 1rem;
        line-height: 1.65;
        color: var(--sl-on-surface);
        max-width: 36rem;
    }
    .exec-header .exec-meta {
        display: flex; flex-direction: column; gap: 0.3rem;
        text-align: right;
        font-family: var(--sl-font-body);
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
        white-space: nowrap;
    }
    .exec-header .exec-meta strong { color: var(--sl-primary); font-weight: 700; }

    /* ---------- KPI Strip (3-up tonal tiles) ---------- */
    .kpi-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1px;
        margin: 0 0 1.8rem 0;
    }
    @media (max-width: 900px) { .kpi-strip { grid-template-columns: 1fr; gap: 0.5rem; } }
    .kpi-strip-item {
        background: var(--sl-surface-low);
        padding: 1.6rem 1.8rem;
        min-height: 168px;
        display: flex; flex-direction: column; justify-content: space-between;
        position: relative; overflow: hidden;
        transition: background-color var(--sl-t);
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) both;
    }
    .kpi-strip-item:hover { background: var(--sl-surface-container); }
    .kpi-strip-item:nth-child(1) { animation-delay: 60ms; }
    .kpi-strip-item:nth-child(2) { animation-delay: 140ms; }
    .kpi-strip-item:nth-child(3) { animation-delay: 220ms; }
    .kpi-strip-head {
        display: flex; justify-content: space-between; align-items: flex-start;
        font-family: var(--sl-font-body);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-on-surface);
    }
    .kpi-strip-head .mat { color: var(--sl-outline); font-size: 18px; }
    .kpi-strip-value {
        font-family: var(--sl-font-display);
        font-size: 2.25rem;
        font-weight: 400;
        font-variation-settings: "opsz" 48;
        line-height: 1;
        letter-spacing: -0.035em;
        color: var(--sl-primary);
        margin: 0 0 0.55rem 0;
    }
    .kpi-strip-value .unit {
        font-family: var(--sl-font-body);
        font-size: 0.86rem;
        font-weight: 500;
        color: var(--sl-outline);
        margin-left: 0.35rem;
        letter-spacing: 0;
    }
    .kpi-strip-delta {
        display: inline-flex; align-items: center; gap: 0.4rem;
        font-family: var(--sl-font-body);
        font-size: 0.82rem;
        color: var(--sl-on-surface-variant);
    }
    .kpi-strip-delta .mat { font-size: 16px; }
    .kpi-strip-delta.warn { color: var(--sl-tertiary-dim); }
    .kpi-strip-delta.ok   { color: var(--sl-primary); }
    .kpi-strip-item.inverse {
        background: linear-gradient(135deg, var(--sl-primary) 0%, var(--sl-primary-container) 100%);
        color: var(--sl-on-primary);
    }
    .kpi-strip-item.inverse .kpi-strip-head,
    .kpi-strip-item.inverse .kpi-strip-head .mat,
    .kpi-strip-item.inverse .kpi-strip-value,
    .kpi-strip-item.inverse .kpi-strip-delta {
        color: var(--sl-on-primary);
    }
    .kpi-strip-item.inverse .kpi-strip-head { opacity: 0.88; }
    .kpi-strip-item.inverse .kpi-strip-delta { opacity: 0.82; }
    .kpi-strip-item.inverse .kpi-strip-value .unit { color: rgba(255,255,255,0.7); }

    /* ---------- Overview Main Bento (narrative + feed + table) ---------- */
    .overview-bento {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1px;
        margin: 0 0 2rem 0;
    }
    @media (max-width: 900px) { .overview-bento { grid-template-columns: 1fr; gap: 0.5rem; } }
    .overview-bento > .narrative-panel   { grid-column: span 2; }
    .overview-bento > .live-feed         { grid-column: span 1; }
    .overview-bento > .activity-panel    { grid-column: span 3; }
    @media (max-width: 900px) {
        .overview-bento > .narrative-panel,
        .overview-bento > .live-feed,
        .overview-bento > .activity-panel { grid-column: span 1; }
    }

    .narrative-panel {
        background: var(--sl-surface-lowest);
        padding: 2rem 2.2rem;
        min-height: 300px;
        display: flex; flex-direction: column;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) 220ms both;
    }
    .narrative-panel .panel-h {
        font-family: var(--sl-font-display);
        font-size: 1.75rem;
        font-weight: 500;
        font-variation-settings: "opsz" 36;
        color: var(--sl-primary);
        letter-spacing: -0.02em;
        margin: 0 0 1.3rem 0;
    }
    .narrative-panel .panel-body {
        font-family: var(--sl-font-body);
        font-size: 1.04rem;
        line-height: 1.75;
        color: var(--sl-on-surface-variant);
        max-width: 46rem;
    }

    .live-feed {
        background: var(--sl-surface-low);
        padding: 2rem 2.2rem;
        min-height: 300px;
        display: flex; flex-direction: column;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) 300ms both;
    }
    .live-feed .feed-head {
        display: flex; justify-content: space-between; align-items: flex-end;
        margin-bottom: 1.3rem;
    }
    .live-feed .feed-h {
        font-family: var(--sl-font-display);
        font-size: 1.4rem;
        font-weight: 500;
        color: var(--sl-primary);
        letter-spacing: -0.02em;
    }
    .live-feed .feed-live {
        display: inline-flex; align-items: center; gap: 0.45rem;
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
    }
    .pulse-dot {
        width: 8px; height: 8px;
        background: var(--sl-primary);
        display: inline-block;
        border-radius: 50%;
        animation: sovereign-pulse 1.6s ease-in-out infinite;
    }
    @keyframes sovereign-pulse {
        0%   { transform: scale(1);   opacity: 0.9; }
        50%  { transform: scale(1.4); opacity: 0.35; }
        100% { transform: scale(1);   opacity: 0.9; }
    }
    .feed-item { margin-bottom: 1.3rem; cursor: default; }
    .feed-item:last-child { margin-bottom: 0; }
    .feed-item .feed-meta {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--sl-outline);
        margin-bottom: 0.35rem;
    }
    .feed-item.alert .feed-meta { color: var(--sl-tertiary-dim); }
    .feed-item .feed-body {
        font-family: var(--sl-font-body);
        font-size: 0.92rem;
        line-height: 1.55;
        color: var(--sl-on-surface);
        transition: color var(--sl-t-fast);
    }
    .feed-item:hover .feed-body { color: var(--sl-primary); }
    .feed-divider {
        height: 0.5px;
        width: 100%;
        background: var(--sl-hairline);
        margin: 0.95rem 0;
    }

    /* ---------- Activity Panel + HTML Table ---------- */
    .activity-panel {
        background: var(--sl-surface-lowest);
        padding: 2rem 2.2rem;
        display: flex; flex-direction: column;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) 380ms both;
    }
    .activity-panel .activity-head {
        display: flex; justify-content: space-between; align-items: flex-end;
        margin-bottom: 1.5rem;
    }
    .activity-panel .activity-h {
        font-family: var(--sl-font-display);
        font-size: 1.75rem;
        font-weight: 500;
        color: var(--sl-primary);
        letter-spacing: -0.02em;
    }
    .activity-panel .activity-link {
        font-family: var(--sl-font-body);
        font-size: 0.78rem;
        color: var(--sl-primary);
        border-bottom: 0.5px solid var(--sl-primary);
        padding-bottom: 1px;
        font-weight: 500;
    }
    .sl-table {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--sl-font-body);
        font-variant-numeric: tabular-nums lining-nums;
    }
    .sl-table thead th {
        text-align: left;
        padding: 0.85rem 1rem;
        font-family: var(--sl-font-body);
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
        background: transparent;
        border: 0;
        border-bottom: 0.5px solid var(--sl-hairline);
        white-space: nowrap;
    }
    .sl-table tbody td {
        padding: 1rem 1rem;
        font-size: 0.88rem;
        color: var(--sl-on-surface);
        background: transparent;
        border: 0;
        border-bottom: 0.5px solid var(--sl-hairline-soft);
        vertical-align: middle;
        line-height: 1.5;
    }
    .sl-table tbody tr { transition: background-color var(--sl-t-fast); }
    .sl-table tbody tr:hover td { background: var(--sl-surface-low); }
    .sl-table tbody tr:last-child td { border-bottom: 0; }
    .sl-table td.meta { color: var(--sl-outline); }
    .sl-table td.strong { font-weight: 600; color: var(--sl-primary); }

    .status-chip {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        background: var(--sl-surface-container);
        color: var(--sl-on-surface);
        border: 0;
    }
    .status-chip.alert { background: #ffdad6; color: #93000a; }
    .status-chip.ok    { background: var(--sl-surface-low); color: var(--sl-primary); }
    .status-chip.warn  { background: rgba(253,182,154,0.22); color: #7a3016; }

    /* ---------- Module header (for Plotly panels) ---------- */
    .module-header {
        display: flex; justify-content: space-between; align-items: flex-end;
        margin: 0.4rem 0 1rem 0;
        padding-bottom: 0.9rem;
        border-bottom: 0.5px solid var(--sl-hairline);
    }
    .module-header .module-h {
        font-family: var(--sl-font-display);
        font-size: 1.5rem;
        font-weight: 500;
        color: var(--sl-primary);
        letter-spacing: -0.02em;
    }
    .module-header .module-legend {
        display: inline-flex; align-items: center; gap: 1.2rem;
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 500;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
    }
    .module-header .module-legend .swatch {
        display: inline-block; width: 10px; height: 10px;
        margin-right: 0.5rem; vertical-align: middle;
        border: 0.5px solid currentColor;
    }

    /* ---------- Simulation observation / narrative block ---------- */
    .sim-observation {
        background: var(--sl-surface-low);
        padding: 1.5rem 1.8rem;
        margin: 0.5rem 0 1.5rem 0;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) 400ms both;
    }
    .sim-observation .obs-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
        margin-bottom: 0.6rem;
    }
    .sim-observation .obs-body {
        font-family: var(--sl-font-body);
        font-size: 0.98rem;
        line-height: 1.7;
        color: var(--sl-on-surface);
    }
    .sim-observation .obs-body strong { color: var(--sl-primary); font-weight: 600; }

    /* ---------- Insight bento (3-up inverse/editorial panels) ---------- */
    .insight-bento {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1px;
        margin: 0.5rem 0 1.5rem 0;
    }
    @media (max-width: 900px) { .insight-bento { grid-template-columns: 1fr; gap: 0.5rem; } }
    .insight-bento > .insight-tile {
        padding: 1.8rem 2rem;
        background: var(--sl-surface-lowest);
        display: flex; flex-direction: column; gap: 0.7rem;
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) both;
    }
    .insight-bento > .insight-tile:nth-child(1) { animation-delay: 60ms;  }
    .insight-bento > .insight-tile:nth-child(2) { animation-delay: 140ms; }
    .insight-bento > .insight-tile:nth-child(3) { animation-delay: 220ms; background: var(--sl-primary); color: var(--sl-on-primary); }
    .insight-bento > .insight-tile:nth-child(3) * { color: var(--sl-on-primary); }
    .insight-tile .tile-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
    }
    .insight-bento > .insight-tile:nth-child(3) .tile-kicker { color: rgba(255,255,255,0.7); }
    .insight-tile .tile-title {
        font-family: var(--sl-font-display);
        font-size: 1.3rem;
        font-weight: 500;
        color: var(--sl-primary);
        letter-spacing: -0.02em;
        line-height: 1.25;
    }
    .insight-tile .tile-body {
        font-family: var(--sl-font-body);
        font-size: 0.92rem;
        line-height: 1.65;
        color: var(--sl-on-surface-variant);
    }
    .insight-bento > .insight-tile:nth-child(3) .tile-body { color: rgba(255,255,255,0.82); }

    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0 !important;
    }
    header[data-testid="stHeader"] [data-testid="stToolbar"] {
        right: 0.75rem; top: 0.5rem;
        background: transparent;
    }
    #MainMenu, footer { visibility: hidden; height: 0; }
    .stDeployButton { display: none !important; }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--sl-background);
        color: var(--sl-on-surface);
        font-family: var(--sl-font-body);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    [data-testid="stAppViewContainer"] .main .block-container {
        padding-top: 2.5rem;
        padding-bottom: 5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 1500px;
    }
    @media (max-width: 1100px) {
        [data-testid="stAppViewContainer"] .main .block-container {
            padding-left: 1.4rem; padding-right: 1.4rem;
        }
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child {
        background: var(--sl-surface-low) !important;
        border-right: 0.5px solid var(--sl-hairline);
        padding-top: 1.6rem;
    }
    [data-testid="stSidebar"]::after { content: none !important; display: none !important; }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: var(--sl-on-surface) !important;
        letter-spacing: 0.005em;
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--sl-primary) !important;
        font-family: var(--sl-font-display) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        fill: var(--sl-primary) !important;
    }

    h1, h2, h3, h4, h5 {
        font-family: var(--sl-font-display);
        font-optical-sizing: auto;
        color: var(--sl-primary);
        font-weight: 500;
        letter-spacing: -0.02em;
    }
    p, li, label, span, button, input, textarea, select {
        font-family: var(--sl-font-body);
    }

    :focus-visible {
        outline: 0.5px solid var(--sl-primary) !important;
        outline-offset: 2px !important;
    }

    .hero-card,
    .metric-card,
    .section-card,
    .note-card,
    .insight-card,
    .brief-meta-card,
    .brief-summary-card,
    .selector-note,
    .sidebar-stat-card,
    .sidebar-note-card {
        background: var(--sl-surface-lowest);
        border: 0.5px solid var(--sl-hairline-soft);
        border-radius: 0;
        box-shadow: none;
        transition: transform var(--sl-t), background-color var(--sl-t), border-color var(--sl-t);
    }
    .metric-card,
    .section-card,
    .insight-card,
    .brief-meta-card {
        animation: sovereign-rise 520ms cubic-bezier(0.2, 0.7, 0.1, 1) both;
    }
    .metric-card:hover,
    .section-card:hover,
    .insight-card:hover,
    .brief-meta-card:hover {
        transform: scale(1.015);
        border-color: var(--sl-hairline);
    }

    .hero-card {
        position: relative;
        padding: 2rem 0 2.4rem 0;
        background: transparent;
        border: 0;
        margin: 0 0 2.2rem 0;
        max-width: 66rem;
        animation: sovereign-fade 500ms ease-out both;
    }
    .hero-masthead {
        display: flex; justify-content: space-between; align-items: center;
        padding-bottom: 1.2rem;
        margin-bottom: 1.6rem;
        border-bottom: 0.5px solid var(--sl-hairline);
        font-family: var(--sl-font-body);
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--sl-on-surface-variant);
    }
    .hero-brand {
        display: inline-flex; align-items: center; gap: 0.7rem;
        color: var(--sl-primary);
        font-weight: 700;
    }
    .hero-brand .mat { color: var(--sl-primary); }
    .hero-brand-meta { color: var(--sl-outline); }
    .hero-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        color: var(--sl-on-surface-variant);
        margin-bottom: 1.2rem;
    }
    .hero-title {
        font-family: var(--sl-font-display);
        font-size: 3.5rem;
        font-weight: 400;
        font-variation-settings: "opsz" 48;
        line-height: 1.04;
        letter-spacing: -0.035em;
        color: var(--sl-primary);
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        font-family: var(--sl-font-body);
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.65;
        color: var(--sl-on-surface-variant);
        max-width: 52rem;
    }

    .brief-summary-card {
        padding: 2rem 2rem 1.8rem 2rem;
        margin-bottom: 1.2rem;
        background: var(--sl-surface-low);
        border: 0;
    }
    .brief-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-on-surface-variant);
        margin-bottom: 0.7rem;
    }
    .brief-name {
        font-family: var(--sl-font-display);
        font-size: 2.2rem;
        font-weight: 500;
        font-variation-settings: "opsz" 48;
        letter-spacing: -0.03em;
        line-height: 1.08;
        color: var(--sl-primary);
        margin-bottom: 0.65rem;
    }
    .brief-summary {
        font-family: var(--sl-font-body);
        font-size: 0.98rem;
        line-height: 1.7;
        color: var(--sl-on-surface-variant);
        max-width: 60rem;
    }
    .brief-meta-card {
        padding: 1.4rem 1.4rem;
        min-height: 118px;
        margin-bottom: 0.7rem;
    }
    .brief-meta-label {
        font-family: var(--sl-font-body);
        font-size: 0.64rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: var(--sl-outline);
        margin-bottom: 0.7rem;
    }
    .brief-meta-value {
        font-family: var(--sl-font-body);
        font-size: 1rem;
        line-height: 1.45;
        color: var(--sl-primary);
        font-weight: 500;
        overflow-wrap: break-word;
    }
    .selector-note {
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
        background: var(--sl-surface-low);
        border: 0;
    }

    .sidebar-rail-title {
        font-family: var(--sl-font-display);
        font-size: 1.6rem;
        font-weight: 700;
        font-variation-settings: "opsz" 24;
        letter-spacing: -0.02em;
        color: var(--sl-primary) !important;
        margin: 0.25rem 0 0.3rem 0;
    }
    .sidebar-stat-card {
        background: var(--sl-surface-lowest);
        border: 0.5px solid var(--sl-hairline-soft);
        border-radius: 0;
        box-shadow: none;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
        color: var(--sl-on-surface) !important;
    }
    .sidebar-note-card {
        background: var(--sl-surface-lowest);
        border: 0;
        border-left: 0.5px solid var(--sl-primary);
        border-radius: 0;
        box-shadow: none;
        padding: 1rem 1.1rem;
        margin: 0.3rem 0 0.8rem 0;
        color: var(--sl-on-surface) !important;
    }
    .sidebar-card-label {
        font-family: var(--sl-font-body);
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        color: var(--sl-outline) !important;
        margin-bottom: 0.7rem;
    }
    .sidebar-card-value {
        font-family: var(--sl-font-display) !important;
        font-size: 2.2rem;
        font-variation-settings: "opsz" 36;
        line-height: 1;
        font-weight: 400;
        letter-spacing: -0.025em;
        color: var(--sl-primary) !important;
        margin-bottom: 0.5rem;
    }
    .sidebar-card-subtitle {
        font-family: var(--sl-font-body);
        font-size: 0.86rem;
        line-height: 1.5;
        color: var(--sl-on-surface-variant) !important;
    }

    .metric-card {
        padding: 1.4rem 1.4rem 1.4rem 1.4rem;
        min-height: 148px;
        margin-bottom: 0.7rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-label {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        color: var(--sl-outline);
        text-transform: uppercase;
        letter-spacing: 0.22em;
        margin-bottom: 0.9rem;
    }
    .metric-value {
        font-family: var(--sl-font-display);
        font-size: 2.4rem;
        font-weight: 400;
        font-variation-settings: "opsz" 48;
        line-height: 1;
        letter-spacing: -0.035em;
        color: var(--sl-primary);
        overflow-wrap: break-word;
        word-break: normal;
    }
    .metric-subtitle {
        font-family: var(--sl-font-body);
        font-size: 0.86rem;
        line-height: 1.55;
        color: var(--sl-on-surface-variant);
        margin-top: 0.9rem;
        overflow-wrap: break-word;
        word-break: normal;
    }

    .section-card,
    .note-card,
    .insight-card {
        padding: 1.5rem 1.6rem;
        margin-bottom: 0.85rem;
    }
    .note-card {
        background: var(--sl-surface-low);
        border: 0;
    }
    .insight-card {
        background: var(--sl-primary);
        border: 0;
        color: var(--sl-on-primary);
    }
    .insight-card .section-title { color: var(--sl-on-primary); }
    .insight-card .section-body { color: rgba(255,255,255,0.82); }
    .section-title {
        font-family: var(--sl-font-display);
        font-size: 1.2rem;
        font-weight: 500;
        font-variation-settings: "opsz" 30;
        letter-spacing: -0.015em;
        color: var(--sl-primary);
        margin-bottom: 0.55rem;
    }
    .section-body {
        font-family: var(--sl-font-body);
        font-size: 0.95rem;
        line-height: 1.7;
        color: var(--sl-on-surface-variant);
    }

    .risk-pill,
    .flag-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        border-radius: 0;
        padding: 0.38rem 0.85rem;
        font-family: var(--sl-font-body);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0.2rem 0.4rem 0.2rem 0;
        border: 0;
        transition: background-color var(--sl-t-fast);
    }
    .risk-pill { color: var(--sl-on-primary); }
    .flag-chip {
        background: var(--sl-surface-low);
        color: var(--sl-primary);
    }

    .section-header {
        font-family: var(--sl-font-display);
        font-size: 1.75rem;
        font-weight: 500;
        font-variation-settings: "opsz" 36;
        letter-spacing: -0.025em;
        color: var(--sl-primary);
        margin: 2rem 0 0.5rem 0;
    }
    .section-subheader {
        font-family: var(--sl-font-body);
        font-size: 0.98rem;
        line-height: 1.65;
        color: var(--sl-on-surface-variant);
        margin-bottom: 1.4rem;
        max-width: 58rem;
    }

    .stTabs {
        counter-reset: chapter;
        margin-top: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap;
        gap: 0 !important;
        margin: 0 0 2rem 0 !important;
        padding: 0 !important;
        border-bottom: 0.5px solid var(--sl-hairline) !important;
        background: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        color: var(--sl-outline) !important;
        padding: 0.95rem 1.3rem !important;
        height: auto !important;
        font-family: var(--sl-font-body) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.22em !important;
        text-transform: uppercase !important;
        cursor: pointer;
        position: relative;
        transition: color var(--sl-t);
        white-space: nowrap;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--sl-primary) !important;
        background: var(--sl-surface-low) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--sl-primary) !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"]::after {
        content: "";
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        bottom: -1px !important;
        top: auto !important;
        height: 2px !important;
        width: auto !important;
        background: var(--sl-primary) !important;
    }
    .stTabs [data-baseweb="tab-panel"] { padding: 0; }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    .stMarkdown p {
        line-height: 1.7;
        color: var(--sl-on-surface-variant);
    }

    div[data-testid="stSelectbox"] > label,
    div[data-testid="stMultiSelect"] > label {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--sl-outline);
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: var(--sl-surface-lowest) !important;
        border: 0 !important;
        border-bottom: 0.5px solid var(--sl-outline-variant) !important;
        border-radius: 0 !important;
        min-height: 46px;
        box-shadow: none !important;
        transition: border-color var(--sl-t);
    }
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: var(--sl-surface-lowest) !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
        border-bottom-color: var(--sl-primary) !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
        border-bottom-color: var(--sl-primary) !important;
        border-bottom-width: 1px !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] span,
    div[data-testid="stSelectbox"] [data-baseweb="select"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] svg,
    div[data-testid="stSelectbox"] [data-baseweb="select"] div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] span,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] input,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] svg,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] div {
        color: var(--sl-primary) !important;
        fill: var(--sl-outline) !important;
        font-family: var(--sl-font-body) !important;
        font-weight: 500 !important;
        -webkit-text-fill-color: var(--sl-primary) !important;
        opacity: 1 !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: var(--sl-surface-low) !important;
        border: 0 !important;
        color: var(--sl-primary) !important;
        border-radius: 0 !important;
        font-family: var(--sl-font-body) !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        color: var(--sl-primary) !important;
        fill: var(--sl-primary) !important;
    }

    div[data-baseweb="popover"] {
        background: var(--sl-surface-lowest) !important;
        border: 0.5px solid var(--sl-hairline-soft) !important;
        border-radius: 0 !important;
        box-shadow: 0 24px 48px rgba(26, 28, 27, 0.06) !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li > div {
        background: var(--sl-surface-lowest) !important;
        color: var(--sl-primary) !important;
        -webkit-text-fill-color: var(--sl-primary) !important;
        font-family: var(--sl-font-body) !important;
    }
    div[data-baseweb="popover"] li {
        transition: background-color var(--sl-t-fast);
    }
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] li:hover {
        background: var(--sl-surface-low) !important;
    }

    div[data-testid="stPlotlyChart"],
    div[data-testid="stDataFrame"] {
        background: var(--sl-surface-lowest);
        border: 0.5px solid var(--sl-hairline-soft);
        border-radius: 0;
        padding: 1rem 1.1rem;
        box-shadow: none;
        transition: background-color var(--sl-t);
    }
    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataFrame"] [role="gridcell"],
    div[data-testid="stDataFrame"] [role="gridcell"] *,
    div[data-testid="stDataFrame"] [role="columnheader"] * {
        color: var(--sl-primary) !important;
        -webkit-text-fill-color: var(--sl-primary) !important;
        font-family: var(--sl-font-body) !important;
    }
    div[data-testid="stPlotlyChart"] > div { overflow: visible !important; }

    .theme-table-wrap {
        background: var(--sl-surface-lowest);
        border: 0.5px solid var(--sl-hairline-soft);
        border-radius: 0;
        box-shadow: none;
        padding: 0;
        overflow: auto;
    }
    .theme-table {
        width: 100%;
        border-collapse: collapse;
        background: transparent;
        color: var(--sl-primary);
        font-family: var(--sl-font-body);
        font-size: 0.92rem;
        font-variant-numeric: tabular-nums lining-nums;
    }
    .theme-table thead th {
        position: sticky;
        top: 0;
        background: var(--sl-surface-low);
        color: var(--sl-outline);
        font-family: var(--sl-font-body);
        text-transform: uppercase;
        letter-spacing: 0.2em;
        font-size: 0.66rem;
        font-weight: 600;
        text-align: left;
        padding: 1rem 1.1rem;
        border: 0;
        border-bottom: 0.5px solid var(--sl-hairline);
        z-index: 1;
        white-space: nowrap;
    }
    .theme-table tbody td {
        background: transparent;
        color: var(--sl-primary);
        padding: 0.9rem 1.1rem;
        border: 0;
        border-bottom: 0.5px solid var(--sl-hairline-soft);
        vertical-align: top;
        line-height: 1.55;
        transition: background-color var(--sl-t-fast);
    }
    .theme-table tbody tr:hover td {
        background: var(--sl-surface-low);
    }
    .theme-table tbody tr:last-child td { border-bottom: 0; }

    .stButton > button,
    .stDownloadButton > button {
        background: var(--sl-primary);
        color: var(--sl-on-primary);
        border: 0;
        border-radius: 0;
        padding: 0.7rem 1.6rem;
        font-family: var(--sl-font-body);
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        cursor: pointer;
        transition: background-color var(--sl-t);
        box-shadow: none;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: var(--sl-primary-container);
        color: var(--sl-on-primary);
    }
    [data-testid="stSidebar"] .stButton > button {
        background: var(--sl-surface-lowest);
        color: var(--sl-primary);
        border: 0.5px solid var(--sl-hairline-soft);
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: var(--sl-surface-highest);
    }

    div[data-testid="stSlider"] [role="slider"] {
        background: var(--sl-primary) !important;
        border: 0 !important;
        border-radius: 0 !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
        background: var(--sl-surface-highest) !important;
        height: 2px !important;
    }

    hr, [data-testid="stMarkdownContainer"] hr {
        border: 0;
        border-top: 0.5px solid var(--sl-hairline);
        margin: 1.8rem 0 1.4rem 0;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.7rem; }

    /* ---------- Compact filter bar (Data Explorer / Portfolio) ---------- */
    .filter-bar {
        border-top: 0.5px solid var(--sl-outline-variant);
        border-bottom: 0.5px solid var(--sl-outline-variant);
        padding: 0.9rem 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        background: var(--sl-background);
        margin: 0.4rem 0 0.5rem 0;
        animation: sovereign-rise 460ms cubic-bezier(0.2, 0.7, 0.1, 1) both;
    }
    .filter-bar .fb-left {
        display: flex; align-items: center;
        flex-wrap: wrap;
        gap: 1.8rem;
    }
    .filter-bar .fb-kicker {
        font-family: var(--sl-font-body);
        font-size: 0.66rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--sl-on-surface-variant);
    }
    .filter-bar .fb-group {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        cursor: default;
        transition: transform var(--sl-t-fast);
    }
    .filter-bar .fb-group:hover { transform: translateY(-1px); }
    .filter-bar .fb-group-label {
        font-family: var(--sl-font-body);
        font-size: 0.84rem;
        color: var(--sl-on-surface-variant);
    }
    .filter-bar .fb-group-value {
        display: inline-flex; align-items: center; gap: 0.25rem;
        border-bottom: 0.5px solid var(--sl-outline-variant);
        padding-bottom: 2px;
        font-family: var(--sl-font-body);
        font-size: 0.88rem;
        font-weight: 500;
        color: var(--sl-primary);
        transition: border-color var(--sl-t-fast);
    }
    .filter-bar .fb-group:hover .fb-group-value { border-bottom-color: var(--sl-primary); }
    .filter-bar .fb-group-value .mat {
        font-size: 18px !important;
        color: var(--sl-on-surface-variant);
        transition: color var(--sl-t-fast);
    }
    .filter-bar .fb-group:hover .fb-group-value .mat { color: var(--sl-primary); }
    .filter-bar .fb-right {
        display: inline-flex;
        align-items: center;
        gap: 1.2rem;
    }
    .filter-bar .fb-action {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-family: var(--sl-font-body);
        font-size: 0.86rem;
        color: var(--sl-on-surface-variant);
        padding: 4px 10px;
        cursor: default;
        transition: color var(--sl-t-fast), background-color var(--sl-t-fast);
    }
    .filter-bar .fb-action:hover { color: var(--sl-primary); }
    .filter-bar .fb-action.primary {
        background: var(--sl-surface-container);
        color: var(--sl-primary);
        padding: 6px 14px;
        border: 0.5px solid transparent;
    }
    .filter-bar .fb-action.primary:hover { background: var(--sl-surface-variant); }
    .filter-bar .fb-action .mat { font-size: 16px !important; }

    .filter-lenses {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 0.25rem 0 0.9rem 0;
    }
    .filter-lenses .lens-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0.8rem;
        background: var(--sl-surface-low);
        border: 0.5px solid var(--sl-outline-variant);
        font-family: var(--sl-font-body);
        font-size: 0.82rem;
        color: var(--sl-primary);
        transition: transform var(--sl-t-fast), background-color var(--sl-t-fast);
        animation: sovereign-rise 420ms cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }
    .filter-lenses .lens-chip:hover {
        transform: translateY(-1px) scale(1.015);
        background: var(--sl-surface-container);
    }
    .filter-lenses .lens-chip .cat {
        color: var(--sl-on-surface-variant);
        font-weight: 500;
    }
    .filter-lenses .lens-chip .mat { font-size: 14px !important; color: var(--sl-on-surface-variant); }

    /* ---------- Rank table (prioritization output) ---------- */
    .sl-table td.rank {
        font-family: var(--sl-font-body);
        font-size: 0.78rem;
        color: var(--sl-on-surface-variant);
        font-variant-numeric: tabular-nums;
        letter-spacing: 0.04em;
    }
    .sl-table td.num {
        text-align: right;
        font-variant-numeric: tabular-nums;
        color: var(--sl-primary);
        font-weight: 500;
    }
    .sl-table td.num.alert { color: #93000a; }
    .sl-table td.center { text-align: center; }
    .status-dot {
        display: inline-block;
        width: 10px; height: 10px;
        border: 0.5px solid var(--sl-outline-variant);
        transition: transform var(--sl-t-fast);
    }
    .sl-table tbody tr:hover .status-dot { transform: scale(1.12); }
    .status-dot.alert   { background: #a64743; }
    .status-dot.warn    { background: #fdb69a; }
    .status-dot.neutral { background: var(--sl-outline); }
    .status-dot.ok      { background: #4f7f80; }

    .pagination-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0.2rem;
        font-family: var(--sl-font-body);
        font-size: 0.86rem;
        color: var(--sl-on-surface-variant);
    }
    .pagination-footer .pf-actions { display: inline-flex; gap: 1.2rem; }
    .pagination-footer .pf-btn {
        display: inline-flex; align-items: center; gap: 0.3rem;
        cursor: default;
        transition: color var(--sl-t-fast);
    }
    .pagination-footer .pf-btn:hover { color: var(--sl-primary); }

    /* ------------------------------------------------------------------
       Master Landing Page — Fairlight Resilience Decision System.
       Top product-name strip → rounded-pill search bar with orange accent →
       centered "Select Entity Context" dropdown. Clean search-and-select
       interface; no metric cards.
       ------------------------------------------------------------------ */

    /* Bounce utility — cubic-bezier(0.175, 0.885, 0.32, 1.275) scale(1.02) */
    .hover-bounce,
    .st-key-landing_search,
    .st-key-landing_directory {
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275),
                    border-color var(--sl-t-fast),
                    box-shadow var(--sl-t-fast),
                    background var(--sl-t-fast);
    }
    .hover-bounce:hover,
    .st-key-landing_search:hover,
    .st-key-landing_directory:hover {
        transform: scale(1.02);
    }

    /* Product-name top strip — chunky chrome header */
    .landing-header-strip {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.5rem;
        padding: 1.1rem 0 1.4rem 0;
        margin: -0.6rem 0 3rem 0;
        border-bottom: 0.5px solid var(--sl-hairline);
    }
    .landing-header-title {
        font-family: var(--sl-font-display);
        font-size: 2.15rem;
        font-weight: 600;
        line-height: 1.1;
        letter-spacing: -0.02em;
        color: var(--sl-primary);
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .landing-header-title:hover {
        transform: scale(1.02);
    }
    .landing-header-eyebrow {
        font-family: var(--sl-font-body);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.26em;
        text-transform: uppercase;
        color: var(--sl-on-surface-variant);
        white-space: nowrap;
    }

    /* Search bar — rounded pill, orange border, search icon only (no button) */
    .st-key-landing_search {
        max-width: 48rem;
        margin: 0.5rem auto 3.5rem auto;
        position: relative;
        background: #ffffff;
        border: 2px solid #FF5722;
        border-radius: 9999px;
        box-shadow: 0 8px 24px rgba(26, 28, 27, 0.04);
        overflow: hidden;
    }
    .st-key-landing_search:focus-within {
        border-color: #E64A19;
        box-shadow: 0 12px 32px rgba(255, 87, 34, 0.12);
    }
    .st-key-landing_search::before {
        content: "search";
        font-family: "Material Symbols Outlined";
        position: absolute;
        left: 1.25rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.25rem;
        color: var(--sl-on-surface-variant);
        pointer-events: none;
        z-index: 2;
        font-variation-settings: "FILL" 0, "wght" 500;
    }
    .st-key-landing_search:focus-within::before {
        color: #FF5722;
    }
    .st-key-landing_search [data-testid="stForm"],
    .st-key-landing_search [data-testid="stForm"] [data-testid="stVerticalBlock"] {
        border: 0;
        padding: 0;
        background: transparent;
        gap: 0;
    }
    .st-key-landing_search [data-testid="stTextInputRootElement"],
    .st-key-landing_search [data-baseweb="input"],
    .st-key-landing_search [data-baseweb="base-input"] {
        background: #ffffff !important;
        border: 0 !important;
        box-shadow: none !important;
    }
    .st-key-landing_search [data-testid="stTextInputRootElement"]:focus-within,
    .st-key-landing_search [data-baseweb="input"]:focus-within,
    .st-key-landing_search [data-baseweb="base-input"]:focus-within {
        box-shadow: none !important;
    }
    .st-key-landing_search [data-testid="stTextInputRootElement"] input,
    .st-key-landing_search [data-baseweb="base-input"] input,
    .st-key-landing_search input[type="text"] {
        font-family: var(--sl-font-body);
        font-size: 1.05rem;
        font-weight: 500;
        padding: 1rem 1.4rem 1rem 3.2rem;
        letter-spacing: -0.005em;
        color: #2b2d2e !important;
        -webkit-text-fill-color: #2b2d2e !important;
        background: #ffffff !important;
        border: 0 !important;
        caret-color: #2b2d2e;
    }
    .st-key-landing_search [data-testid="stTextInputRootElement"] input::placeholder,
    .st-key-landing_search [data-baseweb="base-input"] input::placeholder,
    .st-key-landing_search input[type="text"]::placeholder {
        color: rgba(43, 45, 46, 0.5) !important;
        -webkit-text-fill-color: rgba(43, 45, 46, 0.5) !important;
        opacity: 1;
    }
    .st-key-landing_search [data-testid="stFormSubmitButton"] {
        display: none;
    }

    /* Central "Select Entity Context" focal heading */
    .landing-selector-heading {
        text-align: center;
        max-width: 40rem;
        margin: 0 auto 1.6rem auto;
        animation: sovereign-fade 500ms ease-out both;
    }
    .landing-selector-title {
        font-family: var(--sl-font-display);
        font-size: 3rem;
        font-weight: 400;
        font-variation-settings: "opsz" 48;
        line-height: 1.06;
        letter-spacing: -0.03em;
        color: var(--sl-primary);
        margin: 0 0 1rem 0;
    }
    .landing-selector-subtitle {
        font-family: var(--sl-font-body);
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.55;
        color: var(--sl-on-surface-variant);
        margin: 0;
    }

    /* Organization Selector dropdown (focal point, large pill) */
    .st-key-landing_directory {
        max-width: 40rem;
        margin: 0 auto 4rem auto;
        background: var(--sl-surface-lowest);
        border: 0.5px solid rgba(196, 198, 207, 0.35);
        box-shadow: 0 12px 36px rgba(26, 28, 27, 0.06);
    }
    .st-key-landing_directory:focus-within {
        border-color: var(--sl-primary);
        box-shadow: 0 16px 44px rgba(26, 28, 27, 0.1);
    }
    .st-key-landing_directory [data-testid="stSelectbox"] {
        background: transparent;
        border: 0;
    }
    .st-key-landing_directory [data-testid="stSelectbox"] > label {
        display: none;
    }
    .st-key-landing_directory [data-baseweb="select"] {
        background: transparent;
    }
    .st-key-landing_directory [data-baseweb="select"] > div {
        background: transparent;
        border: 0;
        font-family: var(--sl-font-body);
        font-size: 1.25rem;
        font-weight: 500;
        color: var(--sl-primary);
        padding: 1rem 1.6rem;
        min-height: 4.25rem;
    }
    .st-key-landing_directory [data-baseweb="select"] svg {
        color: var(--sl-primary);
        width: 1.4rem;
        height: 1.4rem;
    }

    @media (max-width: 820px) {
        .hero-title { font-size: 2.2rem; }
        .brief-name { font-size: 1.6rem; }
        .metric-value { font-size: 1.9rem; }
        .hero-card { padding: 1.5rem 1rem; }
        .section-header { font-size: 1.35rem; }
        .stTabs [data-baseweb="tab-list"] { flex-wrap: nowrap; overflow-x: auto; }
        .stTabs [data-baseweb="tab"] { flex: 0 0 auto; }
        .filter-bar { gap: 0.6rem; padding: 0.7rem; }
        .filter-bar .fb-left { gap: 0.9rem; }
        .landing-selector-title { font-size: 2.1rem; }
        .landing-selector-subtitle { font-size: 0.95rem; }
        .landing-header-eyebrow { display: none; }
        .landing-header-title { font-size: 1.55rem; }
        .landing-header-strip { padding: 0.8rem 0 1rem 0; margin-bottom: 2rem; }
        .st-key-landing_directory [data-baseweb="select"] > div { font-size: 1.05rem; padding: 0.8rem 1.2rem; min-height: 3.5rem; }
    }
</style>
"""


def hero_html() -> str:
    return _compact("""
    <div class="hero-card">
        <div class="hero-masthead">
            <div class="hero-brand">
                <span class="mat fill">monitoring</span>
                <span>Fairlight Advisors &nbsp;&middot;&nbsp; Executive Suite</span>
            </div>
            <div class="hero-brand-meta">Institutional Intelligence</div>
        </div>
        <div class="hero-kicker">Institutional Resilience Assessment</div>
        <div class="hero-title">Fairlight Resilience Decision System</div>
        <div class="hero-subtitle">
            A definitive analysis of nonprofit fiscal posture against simulated macroeconomic shocks. The following
            chapters synthesize liquidity, runway, and exposure vectors into a unified risk perspective for judge-level review.
        </div>
    </div>
    """)


def selector_note_html(body: str) -> str:
    return _compact(f"""
    <div class="selector-note">
        <div class="section-body">{body}</div>
    </div>
    """)


def brief_summary_card_html(name: str, summary: str) -> str:
    return _compact(f"""
    <div class="brief-summary-card">
        <div class="brief-kicker">Organization Briefing</div>
        <div class="brief-name">{name}</div>
        <div class="brief-summary">{summary}</div>
    </div>
    """)


def brief_meta_card_html(label: str, value: str) -> str:
    return _compact(f"""
    <div class="brief-meta-card">
        <div class="brief-meta-label">{label}</div>
        <div class="brief-meta-value">{value}</div>
    </div>
    """)


def sidebar_stat_card_html(label: str, value: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="sidebar-card-subtitle">{subtitle}</div>' if subtitle else ""
    return _compact(f"""
    <div class="sidebar-stat-card">
        <div class="sidebar-card-label">{label}</div>
        <div class="sidebar-card-value">{value}</div>
        {subtitle_html}
    </div>
    """)


def sidebar_note_card_html(body: str) -> str:
    return _compact(f"""
    <div class="sidebar-note-card">
        <div class="sidebar-card-subtitle">{body}</div>
    </div>
    """)


def metric_card_html(title: str, value: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""
    return _compact(f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {subtitle_html}
    </div>
    """)


def section_card_html(title: str, body: str) -> str:
    return _compact(f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-body">{body}</div>
    </div>
    """)


def note_card_html(body: str) -> str:
    return _compact(f"""
    <div class="note-card">
        <div class="section-body">{body}</div>
    </div>
    """)


def insight_card_html(title: str, body: str) -> str:
    return _compact(f"""
    <div class="insight-card">
        <div class="section-title">{title}</div>
        <div class="section-body">{body}</div>
    </div>
    """)


def risk_pill_html(bucket: str) -> str:
    color = risk_bucket_color(bucket)
    return f'<span class="risk-pill" style="background:{color};">{bucket}</span>'


def flag_chip_html(label: str) -> str:
    return f'<span class="flag-chip">{label}</span>'


# ---------------------------------------------------------------------------
# Bento Grid helpers — the Sovereign Ledger's core layout primitive.
# Use bento_grid_open(...) / bento_grid_close() around a set of kpi_bento_html
# cards so they land on a true 12-col CSS grid (not st.columns tracks).
# ---------------------------------------------------------------------------

def bento_grid_open(density: str = "default") -> str:
    cls = {
        "tight": "bento-grid tight",
        "airy":  "bento-grid airy",
    }.get(density, "bento-grid")
    return f'<div class="{cls}">'


def bento_grid_close() -> str:
    return "</div>"


def _mat_icon(name: str, filled: bool = False, size: str = "") -> str:
    cls_parts = ["mat"]
    if filled:
        cls_parts.append("fill")
    if size:
        cls_parts.append(size)
    return f'<span class="{" ".join(cls_parts)}">{name}</span>'


def _compact(html: str) -> str:
    """Collapse per-line leading/trailing whitespace from a multi-line HTML template.

    Streamlit's markdown renderer (CommonMark) treats any line beginning with
    four or more spaces as an indented code block. Multi-line f-strings in this
    module are indented for readability, so when the rendered HTML contains a
    blank line followed by indented markup, the second block gets escaped and
    shown verbatim. Flattening to a single line of HTML prevents that without
    changing the DOM semantics.
    """
    return "".join(line.strip() for line in html.splitlines() if line.strip())


def kpi_bento_html(
    kicker: str,
    value: str,
    unit: str = "",
    subtitle: str = "",
    icon: str = "",
    span: int = 4,
    variant: str = "default",
    delta: str = "",
    delta_icon: str = "",
    delta_warn: bool = False,
    progress_pct: float | None = None,
    progress_caption: str = "",
) -> str:
    """Emit a Sovereign Ledger KPI Bento card.

    variant: "default" | "tonal-low" | "tonal-high" | "inverse"
    Pair with bento_grid_open/close. span ∈ 1..12.
    """
    variant_cls = "" if variant == "default" else variant
    span_cls = f"bento-span-{max(1, min(12, int(span)))}"
    icon_html = _mat_icon(icon) if icon else ""
    unit_html = f'<span class="unit">{unit}</span>' if unit else ""
    sub_html = f'<div class="bento-sub">{subtitle}</div>' if subtitle else ""

    delta_html = ""
    if delta:
        delta_cls = "bento-delta warn" if delta_warn else "bento-delta"
        icon_bit = _mat_icon(delta_icon, size="sm") if delta_icon else ""
        delta_html = f'<div class="{delta_cls}">{icon_bit}<span>{delta}</span></div>'

    progress_html = ""
    if progress_pct is not None:
        pct = max(0.0, min(100.0, float(progress_pct)))
        cap = f'<div class="bento-sub" style="font-size:0.72rem;margin-top:0.1rem;">{progress_caption}</div>' if progress_caption else ""
        progress_html = (
            f'<div class="bento-progress"><span style="width:{pct:.1f}%"></span></div>{cap}'
        )

    return _compact(f"""
    <div class="bento-card {variant_cls} {span_cls}">
        {icon_html}
        <div>
            <div class="bento-kicker">{kicker}</div>
            {sub_html}
        </div>
        <div>
            <div class="bento-value">{value}{unit_html}</div>
            {progress_html}
            {delta_html}
        </div>
    </div>
    """)


def narrative_bento_html(
    title: str,
    body: str,
    icon: str = "",
    span: int = 6,
    variant: str = "default",
    footer_left: str = "",
    footer_right: str = "",
) -> str:
    """Larger Bento panel with a narrative body (no big number)."""
    variant_cls = "" if variant == "default" else variant
    span_cls = f"bento-span-{max(1, min(12, int(span)))}"
    icon_html = _mat_icon(icon) if icon else ""
    footer = ""
    if footer_left or footer_right:
        footer = f'<div class="bento-footer"><span>{footer_left}</span><span>{footer_right}</span></div>'
    return _compact(f"""
    <div class="bento-card {variant_cls} {span_cls}">
        {icon_html}
        <div>
            <div class="bento-title">{title}</div>
            <div class="bento-sub">{body}</div>
        </div>
        {footer}
    </div>
    """)


# ---------------------------------------------------------------------------
# Reference Overview primitives: Executive Header, KPI Strip, Narrative panel,
# Live Feed, Activity table. All emit HTML fragments intended to be stitched
# into a single st.markdown call.
# ---------------------------------------------------------------------------

def executive_header_html(title: str, body: str, meta_lines: list[str] | None = None) -> str:
    meta_html = ""
    if meta_lines:
        meta_html = '<div class="exec-meta">' + "".join(f"<span>{line}</span>" for line in meta_lines) + "</div>"
    return _compact(f"""
    <div class="exec-header">
        <div>
            <h1 class="exec-title">{title}</h1>
            <p class="exec-body">{body}</p>
        </div>
        {meta_html}
    </div>
    """)


def kpi_strip_html(items: list[dict]) -> str:
    """Render a 3-up KPI strip. Each item dict accepts:
        label (str, required)
        value (str, required)
        unit  (str, optional)  — small grey suffix inside the value
        icon  (str, optional)  — material symbol name
        delta (str, optional)  — caption below value
        delta_icon (str, optional)
        delta_tone (str, optional) — "warn" | "ok" | "" (neutral)
        inverse (bool, optional) — navy gradient tile
    """
    tiles = []
    for item in items:
        label = item.get("label", "")
        value = item.get("value", "")
        unit = item.get("unit", "")
        icon = item.get("icon", "")
        delta = item.get("delta", "")
        delta_icon = item.get("delta_icon", "")
        delta_tone = item.get("delta_tone", "")
        inverse = bool(item.get("inverse", False))

        icon_html = _mat_icon(icon) if icon else ""
        unit_html = f'<span class="unit">{unit}</span>' if unit else ""
        delta_html = ""
        if delta:
            tone_cls = f" {delta_tone}" if delta_tone else ""
            icon_bit = _mat_icon(delta_icon, size="sm") if delta_icon else ""
            delta_html = f'<div class="kpi-strip-delta{tone_cls}">{icon_bit}<span>{delta}</span></div>'

        tile_cls = "kpi-strip-item inverse" if inverse else "kpi-strip-item"
        tiles.append(_compact(f"""
        <div class="{tile_cls}">
            <div class="kpi-strip-head"><span>{label}</span>{icon_html}</div>
            <div>
                <div class="kpi-strip-value">{value}{unit_html}</div>
                {delta_html}
            </div>
        </div>
        """))
    return '<div class="kpi-strip">' + "".join(tiles) + "</div>"


def narrative_panel_html(title: str, body: str) -> str:
    return _compact(f"""
    <div class="narrative-panel">
        <div class="panel-h">{title}</div>
        <div class="panel-body">{body}</div>
    </div>
    """)


def live_feed_html(title: str, items: list[dict], live: bool = True) -> str:
    """Render the Live Feed column. Each item dict:
        meta  (str)  — timestamp / kicker row, shown tracked-uppercase
        body  (str)  — single-sentence description
        alert (bool) — paints the meta line in tertiary-dim (warning)
    """
    parts = []
    for idx, it in enumerate(items):
        alert_cls = " alert" if it.get("alert") else ""
        parts.append(_compact(f"""
        <div class="feed-item{alert_cls}">
            <div class="feed-meta">{it.get("meta", "")}</div>
            <div class="feed-body">{it.get("body", "")}</div>
        </div>
        """))
        if idx < len(items) - 1:
            parts.append('<div class="feed-divider"></div>')
    live_html = '<span class="feed-live"><span class="pulse-dot"></span>Live</span>' if live else ""
    return _compact(f"""
    <div class="live-feed">
        <div class="feed-head">
            <div class="feed-h">{title}</div>
            {live_html}
        </div>
        <div>{''.join(parts)}</div>
    </div>
    """)


def status_chip_html(label: str, tone: str = "") -> str:
    """tone in {"", "alert", "ok", "warn"}"""
    cls = "status-chip" if not tone else f"status-chip {tone}"
    return f'<span class="{cls}">{label}</span>'


def html_table_html(
    headers: list[str],
    rows: list[list[str]],
    column_classes: list[str] | None = None,
) -> str:
    """Render rows as a Sovereign-styled HTML table.

    column_classes entries may be "" (default), "meta" (outline-colored),
    or "strong" (primary-colored, semibold). Rows should already contain
    rendered HTML strings (so status chips can be pre-rendered via status_chip_html).
    """
    thead = "".join(f"<th>{h}</th>" for h in headers)
    col_cls = column_classes or [""] * len(headers)
    body_rows = []
    for row in rows:
        tds = []
        for idx, cell in enumerate(row):
            cls = col_cls[idx] if idx < len(col_cls) else ""
            cls_attr = f' class="{cls}"' if cls else ""
            tds.append(f"<td{cls_attr}>{cell}</td>")
        body_rows.append("<tr>" + "".join(tds) + "</tr>")
    return _compact(f"""
    <table class="sl-table">
        <thead><tr>{thead}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    """)


def activity_panel_html(title: str, table_html: str, link_label: str = "") -> str:
    link_html = f'<a class="activity-link" href="#">{link_label}</a>' if link_label else ""
    return _compact(f"""
    <div class="activity-panel">
        <div class="activity-head">
            <div class="activity-h">{title}</div>
            {link_html}
        </div>
        <div style="overflow-x:auto;">{table_html}</div>
    </div>
    """)


def module_header_html(title: str, legend: list[dict] | None = None) -> str:
    """Header above a chart module. Legend = [{label, color}]."""
    legend_html = ""
    if legend:
        items = [
            f'<span><span class="swatch" style="background:{it.get("color", "var(--sl-primary)")};color:{it.get("color", "var(--sl-primary)")};"></span>{it.get("label", "")}</span>'
            for it in legend
        ]
        legend_html = f'<div class="module-legend">{"".join(items)}</div>'
    return _compact(f"""
    <div class="module-header">
        <div class="module-h">{title}</div>
        {legend_html}
    </div>
    """)


def sim_observation_html(body: str, kicker: str = "Observation") -> str:
    return _compact(f"""
    <div class="sim-observation">
        <div class="obs-kicker">{kicker}</div>
        <div class="obs-body">{body}</div>
    </div>
    """)


def insight_bento_html(tiles: list[dict]) -> str:
    """tiles = list of {kicker, title, body}. Last tile auto-renders as inverse navy."""
    parts = []
    for t in tiles:
        parts.append(_compact(f"""
        <div class="insight-tile">
            <div class="tile-kicker">{t.get("kicker", "")}</div>
            <div class="tile-title">{t.get("title", "")}</div>
            <div class="tile-body">{t.get("body", "")}</div>
        </div>
        """))
    return '<div class="insight-bento">' + "".join(parts) + "</div>"


def overview_bento_html(narrative_panel: str, live_feed: str, activity_panel: str) -> str:
    return _compact(f"""
    <div class="overview-bento">
        {narrative_panel}
        {live_feed}
        {activity_panel}
    </div>
    """)


def landing_header_strip_html(
    title: str = "Fairlight Resilience Decision System",
    eyebrow: str = "Intelligence &middot; Institutional Terminal",
) -> str:
    """Slim product-name strip above the landing hero."""
    return _compact(f"""
    <div class="landing-header-strip">
        <div class="landing-header-title">{title}</div>
        <div class="landing-header-eyebrow">{eyebrow}</div>
    </div>
    """)


def landing_headline_html(
    title_html: str = "Select Entity Context",
    subtitle: str = "Establish operational parameters before initiating institutional analysis.",
) -> str:
    """Centered focal heading shown above the Organization Selector."""
    subtitle_html = f'<p class="landing-selector-subtitle">{subtitle}</p>' if subtitle else ""
    return _compact(f"""
    <div class="landing-selector-heading">
        <h2 class="landing-selector-title">{title_html}</h2>
        {subtitle_html}
    </div>
    """)


def action_panel_html(title: str, body: str, cta_label: str = "", cta_icon: str = "") -> str:
    """Full-width dark navy Action Panel matching the Sovereign Ledger reference."""
    cta_html = ""
    if cta_label:
        icon = _mat_icon(cta_icon, filled=True, size="sm") if cta_icon else ""
        cta_html = f'<div class="panel-cta">{icon}<span>{cta_label}</span></div>'
    return _compact(f"""
    <div class="action-panel">
        <div class="panel-copy">
            <div class="panel-title">{title}</div>
            <div class="panel-sub">{body}</div>
        </div>
        {cta_html}
    </div>
    """)


def compact_filter_bar_html(
    groups: list[dict],
    actions: list[dict] | None = None,
    kicker: str = "Global Filters",
) -> str:
    """Compact horizontal filter bar with category dropdowns and action buttons.

    groups = [{"label": "Core Analysis", "value": "Macro Stress Scenario"}, ...]
    actions = [{"label": "Clear Filters", "icon": "close"},
               {"label": "Advanced", "icon": "tune", "primary": True}]
    """
    group_html = []
    for g in groups:
        group_html.append(
            f'<div class="fb-group">'
            f'  <span class="fb-group-label">{g.get("label", "")}:</span>'
            f'  <span class="fb-group-value">'
            f'    <span>{g.get("value", "&mdash;")}</span>'
            f'    {_mat_icon("arrow_drop_down")}'
            f'  </span>'
            f'</div>'
        )

    action_html = []
    for a in actions or []:
        cls = "fb-action primary" if a.get("primary") else "fb-action"
        icon_html = _mat_icon(a.get("icon", ""), size="sm") if a.get("icon") else ""
        action_html.append(f'<span class="{cls}">{icon_html}<span>{a.get("label", "")}</span></span>')

    return _compact(f"""
    <div class="filter-bar">
        <div class="fb-left">
            <span class="fb-kicker">{kicker}</span>
            {''.join(group_html)}
        </div>
        <div class="fb-right">
            {''.join(action_html)}
        </div>
    </div>
    """)


def filter_lenses_html(lenses: list[dict]) -> str:
    """Active-filter chip strip shown under the filter bar.

    lenses = [{"category": "Lens", "value": "Systemic Risk"}, ...]
    """
    if not lenses:
        return ""
    chips = []
    for lens in lenses:
        cat = lens.get("category", "")
        val = lens.get("value", "")
        chips.append(
            f'<span class="lens-chip">'
            f'<span class="cat">{cat}:</span>'
            f'<span>{val}</span>'
            f'{_mat_icon("close", size="sm")}'
            f'</span>'
        )
    return f'<div class="filter-lenses">{"".join(chips)}</div>'


def rank_table_html(
    headers: list[str],
    rows: list[list[str]],
    column_classes: list[str] | None = None,
    column_aligns: list[str] | None = None,
) -> str:
    """Variant of html_table_html with numeric-right alignment and rank column support.

    column_classes entries: "", "meta", "strong", "rank", "num", "num alert", "center".
    column_aligns entries: "", "right", "center" applied to <th>.
    """
    col_cls = column_classes or [""] * len(headers)
    col_algn = column_aligns or [""] * len(headers)
    thead_parts = []
    for idx, h in enumerate(headers):
        align = col_algn[idx] if idx < len(col_algn) else ""
        style = f' style="text-align:{align};"' if align else ""
        thead_parts.append(f"<th{style}>{h}</th>")
    body_rows = []
    for row in rows:
        tds = []
        for idx, cell in enumerate(row):
            cls = col_cls[idx] if idx < len(col_cls) else ""
            cls_attr = f' class="{cls}"' if cls else ""
            tds.append(f"<td{cls_attr}>{cell}</td>")
        body_rows.append("<tr>" + "".join(tds) + "</tr>")
    return _compact(f"""
    <table class="sl-table">
        <thead><tr>{''.join(thead_parts)}</tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
    </table>
    """)


def status_dot_html(tone: str = "neutral") -> str:
    """Status indicator dot for the rank table. tone in {alert, warn, neutral, ok}."""
    return f'<span class="status-dot {tone}"></span>'


def pagination_footer_html(showing: str, prev_label: str = "Prev", next_label: str = "Next") -> str:
    return _compact(f"""
    <div class="pagination-footer">
        <span>{showing}</span>
        <div class="pf-actions">
            <span class="pf-btn">{_mat_icon("chevron_left", size="sm")}<span>{prev_label}</span></span>
            <span class="pf-btn"><span>{next_label}</span>{_mat_icon("chevron_right", size="sm")}</span>
        </div>
    </div>
    """)
