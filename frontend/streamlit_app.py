def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Space Grotesk', sans-serif;
        }

        .stApp {
            background: #080c14;
            color: #e2e8f0;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background: #0c1220;
            border-right: 1px solid rgba(99,179,237,0.08);
        }

        [data-testid="stSidebar"] * {
            color: #cbd5e1 !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: #0f1928 !important;
            border: 1px solid rgba(99,179,237,0.15) !important;
            border-radius: 10px !important;
            color: #e2e8f0 !important;
            font-family: 'Space Grotesk', sans-serif !important;
        }

        label, .stSelectbox label, .stTextInput label {
            color: #94a3b8 !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
        }

        div.stButton > button {
            width: 100%;
            border: 1px solid rgba(99,179,237,0.25);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            color: #e2e8f0;
            background: linear-gradient(135deg, #1a3a5c 0%, #0f2440 100%);
            transition: all 0.2s;
            letter-spacing: 0.04em;
        }

        div.stButton > button:hover {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border-color: rgba(99,179,237,0.5);
            color: white;
        }

        .page-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.02em;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }

        .page-title span {
            color: #3b82f6;
        }

        .page-subtitle {
            color: #64748b;
            font-size: 0.95rem;
            margin-bottom: 1.8rem;
        }

        .card {
            border: 1px solid rgba(99,179,237,0.1);
            border-radius: 16px;
            background: #0c1828;
            padding: 20px;
            margin-bottom: 14px;
        }

        .card-sm {
            border: 1px solid rgba(99,179,237,0.1);
            border-radius: 14px;
            background: #0c1828;
            padding: 16px;
            margin-bottom: 12px;
        }

        .section-label {
            font-size: 0.72rem;
            color: #3b82f6;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #f1f5f9;
            font-family: 'JetBrains Mono', monospace;
            line-height: 1;
        }

        .metric-label {
            font-size: 0.72rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .metric-sub {
            font-size: 0.82rem;
            color: #475569;
            margin-top: 6px;
        }

        .signal-action {
            font-size: 2.8rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: -0.02em;
            line-height: 1;
            margin-bottom: 8px;
        }

        .signal-action.buy { color: #22c55e; }
        .signal-action.sell { color: #ef4444; }
        .signal-action.hold { color: #f59e0b; }

        .signal-meta {
            color: #94a3b8;
            font-size: 0.92rem;
            line-height: 1.6;
            margin-bottom: 14px;
        }

        .signal-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        .signal-mini {
            background: #080c14;
            border: 1px solid rgba(99,179,237,0.08);
            border-radius: 10px;
            padding: 12px;
        }

        .signal-mini-label {
            font-size: 0.68rem;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .signal-mini-value {
            font-size: 0.95rem;
            font-weight: 700;
            color: #e2e8f0;
            font-family: 'JetBrains Mono', monospace;
        }

        .workflow-step {
            display: flex;
            gap: 12px;
            align-items: flex-start;
            padding: 10px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
        }

        .workflow-step:last-child { border-bottom: none; }

        .workflow-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #3b82f6;
            margin-top: 6px;
            flex-shrink: 0;
        }

        .workflow-title {
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 700;
            margin-bottom: 3px;
        }

        .workflow-value {
            font-size: 0.9rem;
            color: #cbd5e1;
            line-height: 1.5;
        }

        .reason-step {
            background: #080c14;
            border: 1px solid rgba(99,179,237,0.08);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 8px;
            color: #cbd5e1;
            font-size: 0.92rem;
            line-height: 1.6;
        }

        .reason-step b {
            color: #3b82f6;
            font-family: 'JetBrains Mono', monospace;
        }

        .news-item {
            padding: 12px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
        }

        .news-item:last-child { border-bottom: none; }

        .news-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: #e2e8f0;
            margin-bottom: 5px;
            line-height: 1.4;
        }

        .news-title a {
            color: #e2e8f0;
            text-decoration: none;
        }

        .news-title a:hover { color: #3b82f6; }

        .news-meta {
            font-size: 0.8rem;
            color: #475569;
        }

        .sentiment-pos { color: #22c55e; }
        .sentiment-neg { color: #ef4444; }
        .sentiment-neu { color: #94a3b8; }

        .risk-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(99,179,237,0.06);
            font-size: 0.9rem;
        }

        .risk-row:last-child { border-bottom: none; }
        .risk-key { color: #64748b; font-weight: 600; }
        .risk-val { color: #e2e8f0; font-family: 'JetBrains Mono', monospace; }

        .status-ok { color: #22c55e; font-weight: 700; }
        .status-warn { color: #f59e0b; font-weight: 700; }
        .status-bad { color: #ef4444; font-weight: 700; }

        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            border: 1px solid rgba(99,179,237,0.2);
            background: rgba(99,179,237,0.08);
        }

        .badge-live { color: #22c55e; border-color: rgba(34,197,94,0.3); background: rgba(34,197,94,0.08); }
        .badge-fallback { color: #f59e0b; border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.08); }

        .empty-state {
            border: 1px dashed rgba(99,179,237,0.15);
            border-radius: 20px;
            background: #0c1220;
            padding: 64px 28px;
            text-align: center;
            margin-top: 16px;
        }

        .empty-icon { font-size: 3rem; margin-bottom: 16px; }

        .empty-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 10px;
        }

        .empty-subtitle {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.7;
            max-width: 400px;
            margin: 0 auto;
        }

        .sidebar-logo {
            font-size: 1.1rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.01em;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid rgba(99,179,237,0.1);
        }

        .sidebar-logo span { color: #3b82f6; }

        @media (max-width: 900px) {
            .block-container {
                padding-top: 3.5rem;
            }

            .signal-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .page-title {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
