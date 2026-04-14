from __future__ import annotations

from .logic import risk_bucket_color


GLOBAL_CSS = """
<style>
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #f6f7f9;
        color: #102a43;
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background: #18324a;
        border-right: 0;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #18324a;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #f8fbff;
    }
    [data-testid="stSidebarCollapseButton"] svg {
        fill: #ffffff !important;
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
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 18px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }
    .hero-card {
        padding: 1.25rem 1.4rem;
        border-top: 4px solid #12395b;
        margin-bottom: 0.85rem;
    }
    .hero-kicker {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #486581;
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-size: 2.15rem;
        font-weight: 700;
        line-height: 1.05;
        color: #102a43;
        margin-bottom: 0.35rem;
    }
    .hero-subtitle {
        font-size: 1rem;
        line-height: 1.45;
        color: #52606d;
        max-width: 65rem;
    }
    .brief-kicker {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #486581;
        margin-bottom: 0.3rem;
    }
    .brief-name {
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.15;
        color: #102a43;
        margin-bottom: 0.35rem;
    }
    .brief-summary {
        font-size: 1rem;
        line-height: 1.55;
        color: #52606d;
        max-width: 60rem;
    }
    .brief-summary-card {
        padding: 1.05rem 1.1rem;
        margin-bottom: 0.8rem;
    }
    .brief-meta-card {
        padding: 0.9rem 0.95rem;
        min-height: 110px;
        margin-bottom: 0.55rem;
    }
    .brief-meta-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #7b8794;
        margin-bottom: 0.3rem;
    }
    .brief-meta-value {
        font-size: 0.98rem;
        line-height: 1.35;
        color: #102a43;
        font-weight: 600;
        overflow-wrap: anywhere;
    }
    .selector-note {
        padding: 0.75rem 0.95rem;
        margin-bottom: 0.6rem;
    }
    .sidebar-rail-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0.25rem 0 1.2rem 0;
    }
    .sidebar-stat-card,
    .sidebar-note-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(111, 181, 192, 0.28);
        box-shadow: none;
        color: #ffffff;
    }
    .sidebar-stat-card {
        padding: 1rem 1rem 0.95rem 1rem;
        margin-bottom: 0.85rem;
    }
    .sidebar-note-card {
        padding: 0.9rem 1rem;
        margin-top: 0.3rem;
        margin-bottom: 0.85rem;
        border-left: 4px solid #6ab3c0;
    }
    .sidebar-card-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.76);
        margin-bottom: 0.35rem;
    }
    .sidebar-card-value {
        font-size: 2rem;
        line-height: 1.05;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .sidebar-card-subtitle {
        font-size: 0.9rem;
        line-height: 1.45;
        color: rgba(255, 255, 255, 0.82);
    }
    .metric-card {
        padding: 1rem 1.05rem;
        min-height: 130px;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #7b8794;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.65rem;
        font-weight: 700;
        line-height: 1.15;
        color: #102a43;
        overflow-wrap: anywhere;
    }
    .metric-subtitle {
        font-size: 0.92rem;
        line-height: 1.4;
        color: #52606d;
        margin-top: 0.45rem;
        overflow-wrap: anywhere;
    }
    .section-card,
    .note-card,
    .insight-card {
        padding: 1rem 1.1rem;
        margin-bottom: 0.8rem;
    }
    .section-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 0.32rem;
    }
    .section-body {
        font-size: 0.98rem;
        line-height: 1.55;
        color: #52606d;
    }
    .insight-card .section-body {
        color: #334e68;
    }
    .risk-pill,
    .flag-chip {
        display: inline-block;
        border-radius: 999px;
        padding: 0.32rem 0.7rem;
        font-size: 0.84rem;
        font-weight: 700;
        margin: 0.2rem 0.35rem 0.2rem 0;
        border: 1px solid rgba(16, 42, 67, 0.08);
    }
    .flag-chip {
        background: #f0f4f8;
        color: #243b53;
    }
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #102a43;
        margin: 0.4rem 0 0.5rem 0;
    }
    .section-subheader {
        font-size: 0.95rem;
        color: #52606d;
        margin-bottom: 0.75rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.55rem;
        margin-bottom: 0.9rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 999px;
        color: #486581;
        padding: 0.55rem 1rem;
        height: 44px;
    }
    .stTabs [aria-selected="true"] {
        background: #12395b;
        color: #ffffff;
        border-color: #12395b;
    }
    .stMarkdown p {
        line-height: 1.55;
    }
    div[data-testid="stSelectbox"] > label,
    div[data-testid="stMultiSelect"] > label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #243b53;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 2.3px solid #7f96ab !important;
        border-radius: 12px !important;
        min-height: 52px;
        box-shadow: none !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
        border-color: #12395b !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
        border-color: #12395b !important;
        box-shadow: 0 0 0 3px rgba(18, 57, 91, 0.08) !important;
    }
    div[data-testid="stSelectbox"] [data-baseweb="select"] span,
    div[data-testid="stSelectbox"] [data-baseweb="select"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] svg,
    div[data-testid="stSelectbox"] [data-baseweb="select"] div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] span,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] input,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] svg,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] div {
        color: #102a43 !important;
        fill: #486581 !important;
        font-weight: 600 !important;
        -webkit-text-fill-color: #102a43 !important;
        opacity: 1 !important;
    }
    div[data-testid="stSelectbox"] input,
    div[data-testid="stMultiSelect"] input {
        color: #102a43 !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] {
        background: #eef4f8 !important;
        border: 1px solid #d9e2ec !important;
        color: #12395b !important;
    }
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] span,
    div[data-testid="stMultiSelect"] [data-baseweb="tag"] svg {
        color: #12395b !important;
        fill: #12395b !important;
    }
    div[data-baseweb="popover"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12) !important;
    }
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] li > div {
        background: #ffffff !important;
        color: #102a43 !important;
        -webkit-text-fill-color: #102a43 !important;
    }
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] li:hover {
        background: #eef4f8 !important;
    }
    div[data-testid="stPlotlyChart"],
    div[data-testid="stDataFrame"] {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 18px;
        padding: 0.45rem 0.6rem;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stDataFrame"] [role="columnheader"],
    div[data-testid="stDataFrame"] [role="gridcell"],
    div[data-testid="stDataFrame"] [role="gridcell"] *,
    div[data-testid="stDataFrame"] [role="columnheader"] * {
        color: #102a43 !important;
        -webkit-text-fill-color: #102a43 !important;
    }
    div[data-testid="stPlotlyChart"] > div {
        overflow: visible !important;
    }
    .theme-table-wrap {
        background: #ffffff;
        border: 1px solid #d9e2ec;
        border-radius: 18px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
        padding: 0;
        overflow: auto;
    }
    .theme-table {
        width: 100%;
        border-collapse: collapse;
        background: #ffffff;
        color: #102a43;
        font-size: 0.97rem;
        font-variant-numeric: tabular-nums;
    }
    .theme-table thead th {
        position: sticky;
        top: 0;
        background: #f7fafc;
        color: #5f6c7b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-size: 0.76rem;
        font-weight: 700;
        text-align: left;
        padding: 0.9rem 0.95rem;
        border-bottom: 1px solid #d9e2ec;
        z-index: 1;
        white-space: nowrap;
    }
    .theme-table tbody td {
        background: #ffffff;
        color: #102a43;
        padding: 0.82rem 0.95rem;
        border-bottom: 1px solid #e8edf3;
        vertical-align: top;
        line-height: 1.45;
    }
    .theme-table tbody tr:nth-child(even) td {
        background: #fbfcfe;
    }
    .theme-table tbody tr:hover td {
        background: #f1f6fa;
    }
    .theme-table tbody tr:last-child td {
        border-bottom: none;
    }
    @media (max-width: 720px) {
        .hero-title {
            font-size: 1.75rem;
        }
    }
</style>
"""


def hero_html() -> str:
    return """
    <div class="hero-card">
        <div class="hero-kicker">Fairlight Advisors | Aggie Hack Demo</div>
        <div class="hero-title">Fairlight Resilience Dashboard</div>
        <div class="hero-subtitle">
            Clean, judge-facing decision support built on the retained upgraded logistic backbone and the
            <code>peer_relative_composite</code> label.
        </div>
    </div>
    """


def selector_note_html(body: str) -> str:
    return f"""
    <div class="selector-note">
        <div class="section-body">{body}</div>
    </div>
    """


def brief_summary_card_html(name: str, summary: str) -> str:
    return f"""
    <div class="brief-summary-card">
        <div class="brief-kicker">Company briefing</div>
        <div class="brief-name">{name}</div>
        <div class="brief-summary">{summary}</div>
    </div>
    """


def brief_meta_card_html(label: str, value: str) -> str:
    return f"""
    <div class="brief-meta-card">
        <div class="brief-meta-label">{label}</div>
        <div class="brief-meta-value">{value}</div>
    </div>
    """


def sidebar_stat_card_html(label: str, value: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="sidebar-card-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="sidebar-stat-card">
        <div class="sidebar-card-label">{label}</div>
        <div class="sidebar-card-value">{value}</div>
        {subtitle_html}
    </div>
    """


def sidebar_note_card_html(body: str) -> str:
    return f"""
    <div class="sidebar-note-card">
        <div class="sidebar-card-subtitle">{body}</div>
    </div>
    """


def metric_card_html(title: str, value: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="metric-subtitle">{subtitle}</div>' if subtitle else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {subtitle_html}
    </div>
    """


def section_card_html(title: str, body: str) -> str:
    return f"""
    <div class="section-card">
        <div class="section-title">{title}</div>
        <div class="section-body">{body}</div>
    </div>
    """


def note_card_html(body: str) -> str:
    return f"""
    <div class="note-card">
        <div class="section-body">{body}</div>
    </div>
    """


def insight_card_html(title: str, body: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="section-title">{title}</div>
        <div class="section-body">{body}</div>
    </div>
    """


def risk_pill_html(bucket: str) -> str:
    color = risk_bucket_color(bucket)
    return f'<span class="risk-pill" style="background:{color}; color:#ffffff;">{bucket}</span>'


def flag_chip_html(label: str) -> str:
    return f'<span class="flag-chip">{label}</span>'
