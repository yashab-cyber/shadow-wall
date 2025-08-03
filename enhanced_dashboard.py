"""
Full-Fledged Enterprise Dashboard HTML Template
Professional cybersecurity command center interface
"""

ENHANCED_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShadowWall AI - Enterprise Cybersecurity Command Center</title>
    
    <!-- Enhanced External Libraries -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.min.js"></script>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/particles.js/2.0.0/particles.min.js"></script>
    
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --primary-bg: #0a0e1a;
            --secondary-bg: rgba(15, 23, 42, 0.9);
            --card-bg: rgba(30, 41, 59, 0.8);
            --accent-primary: #00ff88;
            --accent-secondary: #0066ff;
            --danger-color: #ff3366;
            --warning-color: #ffaa00;
            --info-color: #33aaff;
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --border-color: rgba(255, 255, 255, 0.1);
            --glow: 0 0 20px rgba(0, 255, 136, 0.3);
            --shadow-heavy: 0 20px 40px rgba(0, 0, 0, 0.5);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--primary-bg);
            color: var(--text-primary);
            overflow-x: hidden;
            line-height: 1.6;
            position: relative;
        }
        
        #particles-js {
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
            top: 0;
            left: 0;
        }
        
        .dashboard-container {
            display: grid;
            grid-template-columns: 300px 1fr;
            min-height: 100vh;
            backdrop-filter: blur(10px);
        }
        
        .sidebar {
            background: linear-gradient(180deg, var(--secondary-bg) 0%, rgba(15, 23, 42, 0.95) 100%);
            backdrop-filter: blur(20px);
            border-right: 2px solid var(--border-color);
            padding: 24px;
            position: fixed;
            width: 300px;
            height: 100vh;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: var(--shadow-heavy);
        }
        
        .sidebar-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 40px;
            padding: 20px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            border-radius: 16px;
            box-shadow: var(--glow);
            animation: pulse-glow 3s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: var(--glow); }
            50% { box-shadow: 0 0 30px rgba(0, 255, 136, 0.5); }
        }
        
        .sidebar-header .logo {
            width: 48px;
            height: 48px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }
        
        .sidebar-header h2 {
            color: white;
            font-size: 20px;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        
        .nav-section {
            margin-bottom: 32px;
        }
        
        .nav-section-title {
            color: var(--text-secondary);
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 16px;
            padding: 0 16px;
            position: relative;
        }
        
        .nav-section-title::after {
            content: '';
            position: absolute;
            bottom: -8px;
            left: 16px;
            width: 30px;
            height: 2px;
            background: var(--accent-primary);
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px 20px;
            margin: 6px 0;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-weight: 500;
            position: relative;
            overflow: hidden;
        }
        
        .nav-item::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 0;
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            transition: width 0.3s ease;
            z-index: -1;
        }
        
        .nav-item:hover {
            background: var(--card-bg);
            transform: translateX(8px);
            box-shadow: 0 8px 25px rgba(0, 255, 136, 0.2);
        }
        
        .nav-item:hover::before {
            width: 4px;
        }
        
        .nav-item.active {
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            box-shadow: var(--glow);
            transform: translateX(4px);
        }
        
        .nav-item.active::before {
            width: 100%;
        }
        
        .nav-item i {
            width: 24px;
            text-align: center;
            font-size: 16px;
        }
        
        .main-content {
            margin-left: 300px;
            padding: 24px;
            min-height: 100vh;
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.05));
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 32px;
            padding: 32px;
            background: linear-gradient(135deg, var(--card-bg), rgba(30, 41, 59, 0.6));
            border-radius: 20px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-heavy);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-primary));
            animation: scan 3s ease-in-out infinite;
        }
        
        @keyframes scan {
            0%, 100% { transform: translateX(-100%); }
            50% { transform: translateX(100%); }
        }
        
        .header-title h1 {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header-title p {
            color: var(--text-secondary);
            font-size: 16px;
            font-weight: 400;
        }
        
        .status-indicators {
            display: flex;
            gap: 20px;
        }
        
        .status-card {
            background: linear-gradient(135deg, var(--card-bg), rgba(30, 41, 59, 0.6));
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            min-width: 160px;
            border: 1px solid var(--border-color);
            backdrop-filter: blur(15px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .status-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        }
        
        .status-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--glow);
        }
        
        .status-value {
            font-size: 36px;
            font-weight: 800;
            color: var(--accent-primary);
            margin-bottom: 8px;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }
        
        .status-label {
            color: var(--text-secondary);
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .widget {
            background: linear-gradient(135deg, var(--card-bg), rgba(30, 41, 59, 0.6));
            border-radius: 20px;
            padding: 28px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-heavy);
            backdrop-filter: blur(20px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .widget::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .widget:hover {
            transform: translateY(-4px);
            box-shadow: 0 25px 50px rgba(0, 255, 136, 0.1);
        }
        
        .widget:hover::before {
            opacity: 1;
        }
        
        .widget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }
        
        .widget-title {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 700;
            color: var(--text-primary);
        }
        
        .widget-title i {
            color: var(--accent-primary);
        }
        
        .widget-actions {
            display: flex;
            gap: 8px;
        }
        
        .widget-action {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .widget-action:hover {
            background: var(--accent-primary);
            color: white;
            transform: scale(1.1);
        }
        
        .chart-container {
            position: relative;
            height: 350px;
        }
        
        .map-container {
            height: 450px;
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid var(--border-color);
            position: relative;
        }
        
        .network-graph {
            height: 420px;
            border: 2px solid var(--border-color);
            border-radius: 16px;
            background: linear-gradient(135deg, var(--secondary-bg), rgba(15, 23, 42, 0.8));
        }
        
        .threat-list {
            max-height: 380px;
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-primary) var(--secondary-bg);
        }
        
        .threat-list::-webkit-scrollbar {
            width: 6px;
        }
        
        .threat-list::-webkit-scrollbar-track {
            background: var(--secondary-bg);
            border-radius: 3px;
        }
        
        .threat-list::-webkit-scrollbar-thumb {
            background: var(--accent-primary);
            border-radius: 3px;
        }
        
        .threat-item {
            background: linear-gradient(135deg, var(--secondary-bg), rgba(15, 23, 42, 0.8));
            margin: 12px 0;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid var(--danger-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .threat-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .threat-item:hover {
            transform: translateX(8px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
        }
        
        .threat-item:hover::before {
            opacity: 1;
        }
        
        .threat-critical { border-left-color: #dc2626; }
        .threat-high { border-left-color: var(--danger-color); }
        .threat-medium { border-left-color: var(--warning-color); }
        .threat-low { border-left-color: var(--accent-primary); }
        
        .threat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .threat-type {
            font-weight: 700;
            font-size: 18px;
            color: var(--text-primary);
        }
        
        .threat-confidence {
            padding: 6px 12px;
            border-radius: 8px;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color: white;
            font-size: 12px;
            font-weight: 700;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        }
        
        .threat-description {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 12px;
            line-height: 1.5;
        }
        
        .threat-meta {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-secondary);
            align-items: center;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: linear-gradient(135deg, var(--secondary-bg), rgba(15, 23, 42, 0.8));
            padding: 24px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: 0 12px 24px rgba(0, 255, 136, 0.2);
        }
        
        .metric-card:hover::before {
            transform: scaleX(1);
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 800;
            color: var(--accent-primary);
            margin-bottom: 8px;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .real-time-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: var(--accent-primary);
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
            margin-right: 8px;
            box-shadow: 0 0 10px var(--accent-primary);
        }
        
        @keyframes pulse-dot {
            0%, 100% { 
                opacity: 1; 
                transform: scale(1);
                box-shadow: 0 0 10px var(--accent-primary);
            }
            50% { 
                opacity: 0.7; 
                transform: scale(1.2);
                box-shadow: 0 0 20px var(--accent-primary);
            }
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .two-cols {
            grid-template-columns: 1fr 1fr;
        }
        
        .three-cols {
            grid-template-columns: 1fr 1fr 1fr;
        }
        
        .alert-banner {
            background: linear-gradient(135deg, var(--danger-color), #ff6666);
            padding: 20px 28px;
            border-radius: 16px;
            margin-bottom: 24px;
            display: none;
            animation: slideInAlert 0.5s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(255, 51, 102, 0.3);
        }
        
        @keyframes slideInAlert {
            from { 
                transform: translateY(-100%) scale(0.9); 
                opacity: 0; 
            }
            to { 
                transform: translateY(0) scale(1); 
                opacity: 1; 
            }
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .loading::after {
            content: '';
            width: 24px;
            height: 24px;
            border: 3px solid var(--border-color);
            border-top: 3px solid var(--accent-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 16px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .dashboard-section {
            display: none;
            animation: fadeInSection 0.6s ease;
        }
        
        .dashboard-section.active {
            display: block;
        }
        
        @keyframes fadeInSection {
            from { 
                opacity: 0; 
                transform: translateY(30px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        .severity-badge {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .severity-critical {
            background: linear-gradient(135deg, #dc2626, #b91c1c);
            color: white;
            box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
        }
        
        .severity-high {
            background: linear-gradient(135deg, var(--danger-color), #ff5577);
            color: white;
            box-shadow: 0 4px 12px rgba(255, 51, 102, 0.3);
        }
        
        .severity-medium {
            background: linear-gradient(135deg, var(--warning-color), #ffbb33);
            color: white;
            box-shadow: 0 4px 12px rgba(255, 170, 0, 0.3);
        }
        
        .severity-low {
            background: linear-gradient(135deg, var(--accent-primary), #33ff99);
            color: white;
            box-shadow: 0 4px 12px rgba(0, 255, 136, 0.3);
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: var(--secondary-bg);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .data-table th,
        .data-table td {
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        .data-table th {
            background: linear-gradient(135deg, var(--card-bg), rgba(30, 41, 59, 0.8));
            font-weight: 700;
            color: var(--text-primary);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .data-table tr:hover {
            background: rgba(0, 255, 136, 0.05);
        }
        
        .progress-bar {
            width: 100%;
            height: 10px;
            background: var(--secondary-bg);
            border-radius: 5px;
            overflow: hidden;
            margin: 12px 0;
            border: 1px solid var(--border-color);
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            transition: width 0.5s ease;
            box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.2);
        }
        
        /* Responsive Design */
        @media (max-width: 1400px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 1024px) {
            .dashboard-container {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0;
            }
            
            .header {
                flex-direction: column;
                gap: 20px;
                text-align: center;
            }
            
            .status-indicators {
                justify-content: center;
                flex-wrap: wrap;
            }
        }
        
        /* Advanced animations */
        .widget-glow {
            animation: widget-pulse 4s ease-in-out infinite;
        }
        
        @keyframes widget-pulse {
            0%, 100% { box-shadow: var(--shadow-heavy); }
            50% { box-shadow: 0 25px 50px rgba(0, 255, 136, 0.2); }
        }
        
        .cyber-grid::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                linear-gradient(90deg, rgba(0, 255, 136, 0.1) 1px, transparent 1px),
                linear-gradient(rgba(0, 255, 136, 0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            pointer-events: none;
            opacity: 0.3;
        }
    </style>
</head>
<body>
    <div id="particles-js"></div>
    
    <div class="dashboard-container">
        <div class="sidebar cyber-grid" id="sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    <i class="fas fa-shield-alt"></i>
                </div>
                <div>
                    <h2>ShadowWall AI</h2>
                    <small>Enterprise SOC</small>
                </div>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Core Modules</div>
                <div class="nav-item active" onclick="showSection('overview')">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Command Center</span>
                </div>
                <div class="nav-item" onclick="showSection('threats')">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Threat Analysis</span>
                </div>
                <div class="nav-item" onclick="showSection('honeypots')">
                    <i class="fas fa-spider"></i>
                    <span>Honeypot Network</span>
                </div>
                <div class="nav-item" onclick="showSection('network')">
                    <i class="fas fa-network-wired"></i>
                    <span>Network Monitor</span>
                </div>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Intelligence</div>
                <div class="nav-item" onclick="showSection('ai')">
                    <i class="fas fa-brain"></i>
                    <span>AI Insights</span>
                </div>
                <div class="nav-item" onclick="showSection('analytics')">
                    <i class="fas fa-chart-line"></i>
                    <span>Advanced Analytics</span>
                </div>
                <div class="nav-item" onclick="showSection('reports')">
                    <i class="fas fa-file-alt"></i>
                    <span>Intelligence Reports</span>
                </div>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">Operations</div>
                <div class="nav-item" onclick="showSection('incidents')">
                    <i class="fas fa-fire"></i>
                    <span>Incident Response</span>
                </div>
                <div class="nav-item" onclick="showSection('forensics')">
                    <i class="fas fa-search"></i>
                    <span>Digital Forensics</span>
                </div>
                <div class="nav-item" onclick="showSection('compliance')">
                    <i class="fas fa-clipboard-check"></i>
                    <span>Compliance</span>
                </div>
            </div>
            
            <div class="nav-section">
                <div class="nav-section-title">System</div>
                <div class="nav-item" onclick="showSection('settings')">
                    <i class="fas fa-cog"></i>
                    <span>Configuration</span>
                </div>
                <div class="nav-item" onclick="showSection('alerts')">
                    <i class="fas fa-bell"></i>
                    <span>Alert Center</span>
                </div>
                <div class="nav-item" onclick="showSection('logs')">
                    <i class="fas fa-list-alt"></i>
                    <span>System Logs</span>
                </div>
            </div>
        </div>
        
        <div class="main-content cyber-grid">
            <div class="alert-banner" id="alertBanner">
                <i class="fas fa-exclamation-circle"></i>
                <strong>⚠️ CRITICAL SECURITY ALERT:</strong> Advanced Persistent Threat detected - Immediate SOC response required
            </div>
            
            <div class="header">
                <div class="header-title">
                    <h1><i class="fas fa-shield-alt"></i> Enterprise Cybersecurity Command Center</h1>
                    <p>Real-time threat intelligence • AI-powered analysis • Advanced security monitoring</p>
                </div>
                <div class="status-indicators">
                    <div class="status-card">
                        <div class="status-value" id="activeThreats">--</div>
                        <div class="status-label">Active Threats</div>
                    </div>
                    <div class="status-card">
                        <div class="status-value" id="systemHealth">--</div>
                        <div class="status-label">System Health</div>
                    </div>
                    <div class="status-card">
                        <div class="status-value">
                            <span class="real-time-indicator"></span>LIVE
                        </div>
                        <div class="status-label">Real-time Status</div>
                    </div>
                </div>
            </div>
"""

def get_dashboard_sections():
    return """
            <!-- Command Center Overview -->
            <div id="overview-section" class="dashboard-section active">
                <div class="dashboard-grid">
                    <div class="widget widget-glow">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-globe-americas"></i>
                                Global Threat Intelligence Map
                            </div>
                            <div class="widget-actions">
                                <div class="widget-action" title="Fullscreen">
                                    <i class="fas fa-expand"></i>
                                </div>
                                <div class="widget-action" title="Refresh">
                                    <i class="fas fa-sync"></i>
                                </div>
                            </div>
                        </div>
                        <div id="threatMap" class="map-container"></div>
                    </div>
                    
                    <div class="widget">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-chart-line"></i>
                                Real-time Threat Timeline
                            </div>
                            <div class="widget-actions">
                                <div class="widget-action" title="Configure">
                                    <i class="fas fa-cog"></i>
                                </div>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="timelineChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="widget">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-project-diagram"></i>
                                Network Security Topology
                            </div>
                            <div class="widget-actions">
                                <div class="widget-action" title="Auto-layout">
                                    <i class="fas fa-magic"></i>
                                </div>
                            </div>
                        </div>
                        <div id="networkGraph" class="network-graph"></div>
                    </div>
                    
                    <div class="widget">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-exclamation-triangle"></i>
                                Critical Threat Feed
                            </div>
                            <div class="widget-actions">
                                <div class="widget-action" title="Filter">
                                    <i class="fas fa-filter"></i>
                                </div>
                            </div>
                        </div>
                        <div id="threatList" class="threat-list loading">Initializing threat intelligence feed...</div>
                    </div>
                    
                    <div class="widget">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-spider"></i>
                                Honeypot Activity Monitor
                            </div>
                            <div class="widget-actions">
                                <div class="widget-action" title="Deploy New">
                                    <i class="fas fa-plus"></i>
                                </div>
                            </div>
                        </div>
                        <div id="honeypotList" class="threat-list loading">Loading honeypot network status...</div>
                    </div>
                    
                    <div class="widget">
                        <div class="widget-header">
                            <div class="widget-title">
                                <i class="fas fa-chart-pie"></i>
                                Attack Vector Analysis
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="attackVectorChart"></canvas>
                        </div>
                    </div>
                </div>
                
                <div class="widget full-width">
                    <div class="widget-header">
                        <div class="widget-title">
                            <i class="fas fa-dashboard"></i>
                            Enterprise Security Metrics Dashboard
                        </div>
                        <div class="widget-actions">
                            <div class="widget-action" title="Export Report">
                                <i class="fas fa-download"></i>
                            </div>
                            <div class="widget-action" title="Configure KPIs">
                                <i class="fas fa-sliders-h"></i>
                            </div>
                        </div>
                    </div>
                    <div id="securityMetrics" class="metrics-grid loading">Loading comprehensive security metrics...</div>
                </div>
            </div>
            
            <!-- Additional sections with placeholder content -->
            <div id="threats-section" class="dashboard-section">
                <div class="widget full-width">
                    <div class="widget-header">
                        <div class="widget-title">
                            <i class="fas fa-shield-alt"></i>
                            Advanced Threat Analysis Center
                        </div>
                    </div>
                    <div class="dashboard-grid two-cols">
                        <div class="widget">
                            <div class="widget-title">
                                <i class="fas fa-chart-bar"></i>
                                Threat Classification Matrix
                            </div>
                            <canvas id="threatMatrix"></canvas>
                        </div>
                        <div class="widget">
                            <div class="widget-title">
                                <i class="fas fa-crosshairs"></i>
                                Attack Vector Distribution
                            </div>
                            <canvas id="vectorDistribution"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="ai-section" class="dashboard-section">
                <div class="widget full-width">
                    <div class="widget-header">
                        <div class="widget-title">
                            <i class="fas fa-brain"></i>
                            AI-Powered Security Intelligence
                        </div>
                    </div>
                    <div class="dashboard-grid three-cols">
                        <div class="widget">
                            <div class="widget-title">
                                <i class="fas fa-robot"></i>
                                ML Model Performance
                            </div>
                            <div id="mlPerformance" class="loading">Analyzing ML models...</div>
                        </div>
                        <div class="widget">
                            <div class="widget-title">
                                <i class="fas fa-crystal-ball"></i>
                                Threat Predictions
                            </div>
                            <div id="threatPredictions" class="loading">Computing predictions...</div>
                        </div>
                        <div class="widget">
                            <div class="widget-title">
                                <i class="fas fa-chart-area"></i>
                                Anomaly Detection
                            </div>
                            <canvas id="anomalyChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""

def get_dashboard_scripts():
    return """
    <script>
        // Enhanced global variables
        let charts = {};
        let map = null;
        let network = null;
        let ws = null;
        let currentSection = 'overview';
        
        // Initialize enhanced dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeParticles();
            initializeDashboard();
            connectWebSocket();
            setInterval(updateLiveData, 15000); // More frequent updates
            startAdvancedAnimations();
        });
        
        function initializeParticles() {
            particlesJS('particles-js', {
                particles: {
                    number: { value: 50, density: { enable: true, value_area: 800 } },
                    color: { value: '#00ff88' },
                    shape: { type: 'circle' },
                    opacity: { value: 0.3, random: true },
                    size: { value: 2, random: true },
                    line_linked: { 
                        enable: true, 
                        distance: 150, 
                        color: '#00ff88', 
                        opacity: 0.2, 
                        width: 1 
                    },
                    move: { 
                        enable: true, 
                        speed: 1, 
                        direction: 'none', 
                        random: false, 
                        straight: false, 
                        out_mode: 'out', 
                        bounce: false 
                    }
                },
                interactivity: {
                    detect_on: 'canvas',
                    events: { 
                        onhover: { enable: true, mode: 'repulse' },
                        onclick: { enable: true, mode: 'push' },
                        resize: true 
                    }
                },
                retina_detect: true
            });
        }
        
        function initializeDashboard() {
            loadDashboardData();
            initializeMap();
            initializeCharts();
            initializeNetworkTopology();
        }
        
        async function loadDashboardData() {
            try {
                const response = await fetch('/api/dashboard-data');
                const data = await response.json();
                
                updateThreatList(data.threats);
                updateHoneypotList(data.honeypots);
                updateSecurityMetrics(data);
                updateStatusIndicators(data);
                updateThreatMap(data.threat_map);
                updateTimelineChart(data.timeline);
                
                // Load additional data
                await loadAdvancedMetrics();
                
            } catch (error) {
                console.error('Error loading dashboard data:', error);
                showErrorNotification('Failed to load dashboard data');
            }
        }
        
        async function loadAdvancedMetrics() {
            try {
                const [mlData, securityData, networkData] = await Promise.all([
                    fetch('/api/ml-insights').then(r => r.json()),
                    fetch('/api/security-metrics').then(r => r.json()),
                    fetch('/api/network-stats').then(r => r.json())
                ]);
                
                updateMLInsights(mlData);
                updateAdvancedSecurityMetrics(securityData);
                updateNetworkStats(networkData);
                
            } catch (error) {
                console.error('Error loading advanced metrics:', error);
            }
        }
        
        function initializeMap() {
            map = L.map('threatMap', {
                zoomControl: false,
                attributionControl: false
            }).setView([20, 0], 2);
            
            // Dark theme map
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: '© CARTO'
            }).addTo(map);
            
            // Add custom controls
            L.control.zoom({ position: 'topright' }).addTo(map);
        }
        
        function updateThreatMap(locations) {
            if (!map || !locations) return;
            
            locations.forEach(location => {
                const intensity = location.threat_count;
                const color = intensity > 15 ? '#ff3366' : 
                             intensity > 10 ? '#ff6600' : 
                             intensity > 5 ? '#ffaa00' : '#00ff88';
                
                const circle = L.circle([location.latitude, location.longitude], {
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.6,
                    radius: Math.max(50000, intensity * 15000),
                    weight: 2
                }).addTo(map);
                
                circle.bindPopup(`
                    <div style="background: #0a0e1a; color: white; padding: 12px; border-radius: 8px; border: 1px solid #00ff88;">
                        <h4 style="color: #00ff88; margin-bottom: 8px;">${location.country}</h4>
                        <p><strong>Threats:</strong> ${location.threat_count}</p>
                        <p><strong>Latest:</strong> ${location.latest_threat || 'N/A'}</p>
                        <p><strong>Risk Level:</strong> ${intensity > 15 ? 'Critical' : intensity > 10 ? 'High' : intensity > 5 ? 'Medium' : 'Low'}</p>
                    </div>
                `, {
                    closeButton: false,
                    offset: [0, -10]
                });
                
                // Add pulsing effect for high-threat areas
                if (intensity > 10) {
                    circle.setStyle({ className: 'pulse-marker' });
                }
            });
        }
        
        function initializeCharts() {
            // Enhanced timeline chart
            const timelineCtx = document.getElementById('timelineChart').getContext('2d');
            charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Threats Detected',
                        data: [],
                        borderColor: '#ff3366',
                        backgroundColor: 'rgba(255, 51, 102, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#ff3366',
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            labels: { 
                                color: 'white',
                                font: { size: 14, weight: 'bold' }
                            } 
                        }
                    },
                    scales: {
                        x: { 
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: { 
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    }
                }
            });
            
            // Attack vector chart
            const vectorCtx = document.getElementById('attackVectorChart');
            if (vectorCtx) {
                charts.attackVector = new Chart(vectorCtx.getContext('2d'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Network', 'Web', 'Email', 'Social', 'Physical'],
                        datasets: [{
                            data: [45, 25, 15, 10, 5],
                            backgroundColor: [
                                '#ff3366',
                                '#ffaa00', 
                                '#00ff88',
                                '#33aaff',
                                '#9966ff'
                            ],
                            borderWidth: 3,
                            borderColor: '#0a0e1a'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { 
                                    color: 'white',
                                    padding: 20,
                                    font: { size: 12, weight: 'bold' }
                                }
                            }
                        }
                    }
                });
            }
        }
        
        function updateTimelineChart(timelineData) {
            if (!charts.timeline || !timelineData) return;
            
            const labels = timelineData.map(item => {
                const date = new Date(item.timestamp);
                return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            });
            const data = timelineData.map(item => item.count);
            
            charts.timeline.data.labels = labels;
            charts.timeline.data.datasets[0].data = data;
            charts.timeline.update('active');
        }
        
        function updateThreatList(threats) {
            const container = document.getElementById('threatList');
            if (!threats || threats.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #94a3b8;"><i class="fas fa-shield-alt" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i><p>No active threats detected</p><p style="font-size: 12px;">All systems secure</p></div>';
                return;
            }
            
            container.innerHTML = threats.map(threat => `
                <div class="threat-item threat-${threat.severity || 'low'}">
                    <div class="threat-header">
                        <div class="threat-type">${threat.type || 'Unknown Threat'}</div>
                        <div class="threat-confidence">${(threat.confidence * 100).toFixed(1)}%</div>
                    </div>
                    <div class="threat-description">${threat.description || 'Advanced threat detected by AI security system'}</div>
                    <div class="threat-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${threat.source_ip || 'Unknown'}</span>
                        <span><i class="fas fa-clock"></i> ${new Date(threat.timestamp).toLocaleTimeString()}</span>
                        <span class="severity-badge severity-${threat.severity || 'low'}">${(threat.severity || 'low').toUpperCase()}</span>
                    </div>
                </div>
            `).join('');
        }
        
        function updateHoneypotList(honeypots) {
            const container = document.getElementById('honeypotList');
            if (!honeypots || honeypots.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px; color: #94a3b8;"><i class="fas fa-spider" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i><p>No honeypot activity</p><p style="font-size: 12px;">All traps are active</p></div>';
                return;
            }
            
            container.innerHTML = honeypots.map(event => `
                <div class="threat-item">
                    <div class="threat-header">
                        <div class="threat-type">${event.service || 'Unknown Service'} Honeypot</div>
                        <div style="padding: 4px 8px; background: #00ff88; color: #0a0e1a; border-radius: 6px; font-size: 11px; font-weight: bold;">CAPTURED</div>
                    </div>
                    <div class="threat-description">Action: ${event.action || 'Connection attempt detected'}</div>
                    <div class="threat-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${event.source_ip || 'Unknown'}</span>
                        <span><i class="fas fa-clock"></i> ${new Date(event.timestamp).toLocaleTimeString()}</span>
                        <span><i class="fas fa-database"></i> Data captured</span>
                    </div>
                </div>
            `).join('');
        }
        
        function updateSecurityMetrics(data) {
            const container = document.getElementById('securityMetrics');
            const metrics = [
                { label: 'Total Threats', value: data.threats ? data.threats.length : 0, icon: 'exclamation-triangle', color: '#ff3366' },
                { label: 'Honeypot Events', value: data.honeypots ? data.honeypots.length : 0, icon: 'spider', color: '#00ff88' },
                { label: 'Network Connections', value: data.network_stats ? data.network_stats.connections_tracked || 0 : 0, icon: 'network-wired', color: '#33aaff' },
                { label: 'Detection Rate', value: '94.2%', icon: 'crosshairs', color: '#00ff88' },
                { label: 'Response Time', value: '2.3min', icon: 'stopwatch', color: '#ffaa00' },
                { label: 'System Uptime', value: '99.7%', icon: 'server', color: '#00ff88' },
                { label: 'Blocked Attacks', value: Math.floor(Math.random() * 1000), icon: 'shield-alt', color: '#ff3366' },
                { label: 'False Positives', value: '< 3%', icon: 'balance-scale', color: '#9966ff' }
            ];
            
            container.innerHTML = metrics.map(metric => `
                <div class="metric-card">
                    <div style="color: ${metric.color}; font-size: 24px; margin-bottom: 12px;">
                        <i class="fas fa-${metric.icon}"></i>
                    </div>
                    <div class="metric-value" style="color: ${metric.color};">${metric.value}</div>
                    <div class="metric-label">${metric.label}</div>
                </div>
            `).join('');
        }
        
        function updateStatusIndicators(data) {
            const activeThreats = data.threats ? data.threats.filter(t => t.active).length : 0;
            document.getElementById('activeThreats').textContent = activeThreats;
            document.getElementById('systemHealth').textContent = '98.5%';
            
            // Add dynamic coloring based on threat level
            const threatElement = document.getElementById('activeThreats');
            if (activeThreats > 10) {
                threatElement.style.color = '#ff3366';
            } else if (activeThreats > 5) {
                threatElement.style.color = '#ffaa00';
            } else {
                threatElement.style.color = '#00ff88';
            }
        }
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'live_update') {
                    updateLiveData(data.data);
                }
            };
            
            ws.onclose = function() {
                setTimeout(connectWebSocket, 5000);
                showErrorNotification('Connection lost - attempting to reconnect...');
            };
            
            ws.onopen = function() {
                console.log('Real-time connection established');
            };
        }
        
        function updateLiveData(data) {
            if (data) {
                document.getElementById('activeThreats').textContent = data.active_threats || 0;
                
                // Show critical alert for high threat activity
                if (data.active_threats > 5) {
                    document.getElementById('alertBanner').style.display = 'block';
                    startCriticalAlertAnimation();
                }
                
                // Update other live indicators
                updateSystemLoadIndicator(data.system_load);
            }
        }
        
        function showSection(sectionName) {
            // Hide all sections
            document.querySelectorAll('.dashboard-section').forEach(section => {
                section.classList.remove('active');
                section.style.display = 'none';
            });
            
            // Show selected section
            const targetSection = document.getElementById(sectionName + '-section');
            if (targetSection) {
                targetSection.style.display = 'block';
                setTimeout(() => targetSection.classList.add('active'), 50);
            }
            
            // Update nav items
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
            
            currentSection = sectionName;
            
            // Load section-specific data
            loadSectionData(sectionName);
        }
        
        function loadSectionData(section) {
            switch(section) {
                case 'ai':
                    loadAIInsights();
                    break;
                case 'analytics':
                    loadAdvancedAnalytics();
                    break;
                case 'threats':
                    loadThreatAnalysis();
                    break;
            }
        }
        
        function initializeNetworkTopology() {
            setTimeout(() => {
                fetch('/api/network-topology')
                    .then(response => response.json())
                    .then(data => {
                        const container = document.getElementById('networkGraph');
                        if (!container) return;
                        
                        const nodes = new vis.DataSet(data.nodes.map(node => ({
                            ...node,
                            font: { color: 'white', size: 14 },
                            shadow: true,
                            borderWidth: 2,
                            borderColor: node.color
                        })));
                        
                        const edges = new vis.DataSet(data.edges.map(edge => ({
                            ...edge,
                            width: edge.traffic === 'high' ? 4 : edge.traffic === 'medium' ? 2 : 1,
                            shadow: true,
                            smooth: { type: 'continuous' }
                        })));
                        
                        const networkData = { nodes, edges };
                        
                        const options = {
                            nodes: {
                                shape: 'dot',
                                size: 25,
                                font: { color: 'white', size: 12 },
                                borderWidth: 2,
                                shadow: true
                            },
                            edges: {
                                width: 2,
                                shadow: true,
                                smooth: true
                            },
                            physics: {
                                stabilization: { iterations: 100 },
                                barnesHut: { gravitationalConstant: -2000 }
                            },
                            interaction: {
                                hover: true,
                                tooltipDelay: 200
                            }
                        };
                        
                        network = new vis.Network(container, networkData, options);
                        
                        // Add network events
                        network.on('click', function(params) {
                            if (params.nodes.length > 0) {
                                const nodeId = params.nodes[0];
                                showNodeDetails(nodeId);
                            }
                        });
                    })
                    .catch(error => console.error('Error loading network topology:', error));
            }, 1000);
        }
        
        function startAdvancedAnimations() {
            // Add subtle animations to enhance the cybersecurity feel
            setInterval(() => {
                const widgets = document.querySelectorAll('.widget');
                const randomWidget = widgets[Math.floor(Math.random() * widgets.length)];
                if (randomWidget && Math.random() > 0.7) {
                    randomWidget.classList.add('widget-glow');
                    setTimeout(() => randomWidget.classList.remove('widget-glow'), 2000);
                }
            }, 5000);
        }
        
        function startCriticalAlertAnimation() {
            const alertBanner = document.getElementById('alertBanner');
            alertBanner.style.animation = 'none';
            setTimeout(() => {
                alertBanner.style.animation = 'slideInAlert 0.5s ease';
            }, 10);
        }
        
        function showErrorNotification(message) {
            // Create and show error notification
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: linear-gradient(135deg, #ff3366, #ff6666);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(255, 51, 102, 0.3);
                z-index: 10000;
                animation: slideInAlert 0.5s ease;
            `;
            notification.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 5000);
        }
        
        // Initialize dashboard when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initializeDashboard);
        } else {
            initializeDashboard();
        }
    </script>
</body>
</html>
"""
