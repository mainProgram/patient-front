#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

def generate_html_report(json_file):
    """Générer un rapport HTML à partir du fichier JSON des tests"""

    # Charger les données JSON
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Analyser les résultats
    total_tests = data['summary']['total_tests']
    passed = data['summary']['passed']
    failed = data['summary']['failed']
    success_rate = float(data['summary']['success_rate'].rstrip('%'))

    # Classifier les vulnérabilités
    vulnerabilities = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }

    for test in data['test_results']:
        if not test['passed']:
            if 'SQL' in test['test'] and 'Redirection non autorisée' in test['details']:
                vulnerabilities['critical'].append(test)
            elif 'bypass' in test['test'] and 'Redirection non autorisée' in test['details']:
                vulnerabilities['high'].append(test)
            elif 'XSS' in test['test']:
                vulnerabilities['high'].append(test)
            else:
                vulnerabilities['medium'].append(test)

    # Générer le HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Sécurité - Authentification</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.2em;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .summary-card:hover {{
            transform: translateY(-5px);
        }}

        .summary-card .value {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .summary-card.success .value {{
            color: #10b981;
        }}

        .summary-card.danger .value {{
            color: #ef4444;
        }}

        .summary-card.warning .value {{
            color: #f59e0b;
        }}

        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}

        .section h2 {{
            color: #4a5568;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }}

        .vulnerability-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .vuln-card {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.3s ease;
        }}

        .vuln-card.critical {{
            border-left: 5px solid #dc2626;
            background: #fef2f2;
        }}

        .vuln-card.high {{
            border-left: 5px solid #ea580c;
            background: #fff7ed;
        }}

        .vuln-card.medium {{
            border-left: 5px solid #f59e0b;
            background: #fffbeb;
        }}

        .vuln-card.low {{
            border-left: 5px solid #10b981;
            background: #f0fdf4;
        }}

        .vuln-card h3 {{
            margin-bottom: 10px;
            color: #1f2937;
        }}

        .vuln-card .details {{
            color: #6b7280;
            font-size: 0.9em;
            margin-top: 10px;
        }}

        .recommendations {{
            background: #eff6ff;
            border: 1px solid #3b82f6;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }}

        .recommendations h3 {{
            color: #1e40af;
            margin-bottom: 15px;
        }}

        .recommendations ul {{
            list-style: none;
            padding-left: 0;
        }}

        .recommendations li {{
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
        }}

        .recommendations li:before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #3b82f6;
            font-weight: bold;
        }}

        .code-example {{
            background: #1f2937;
            color: #e5e7eb;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
            overflow-x: auto;
        }}

        .code-example pre {{
            margin: 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        .test-results {{
            margin-top: 20px;
        }}

        .test-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
            transition: background 0.2s ease;
        }}

        .test-item:hover {{
            background: #f9fafb;
        }}

        .test-item .status {{
            font-size: 1.5em;
            margin-right: 15px;
        }}

        .test-item.passed .status {{
            color: #10b981;
        }}

        .test-item.failed .status {{
            color: #ef4444;
        }}

        .test-item .name {{
            flex: 1;
            font-weight: 500;
        }}

        .test-item .details {{
            color: #6b7280;
            font-size: 0.9em;
        }}

        .severity-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            margin-right: 10px;
        }}

        .severity-badge.critical {{
            background: #dc2626;
            color: white;
        }}

        .severity-badge.high {{
            background: #ea580c;
            color: white;
        }}

        .severity-badge.medium {{
            background: #f59e0b;
            color: white;
        }}

        .severity-badge.low {{
            background: #10b981;
            color: white;
        }}

        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
            font-size: 0.9em;
        }}

        @media print {{
            body {{
                background: white;
            }}
            .section {{
                box-shadow: none;
                border: 1px solid #e5e7eb;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Rapport de Sécurité - Authentification</h1>
            <div class="subtitle">
                Application de Gestion des Patients | {data['date']}
            </div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>Tests Totaux</h3>
                <div class="value">{total_tests}</div>
                <p>Scénarios testés</p>
            </div>

            <div class="summary-card success">
                <h3>Tests Réussis</h3>
                <div class="value">{passed}</div>
                <p>Protections efficaces</p>
            </div>

            <div class="summary-card danger">
                <h3>Tests Échoués</h3>
                <div class="value">{failed}</div>
                <p>Vulnérabilités détectées</p>
            </div>

            <div class="summary-card {'warning' if success_rate < 70 else 'success'}">
                <h3>Taux de Réussite</h3>
                <div class="value">{success_rate:.1f}%</div>
                <p>Score de sécurité</p>
            </div>
        </div>

        <div class="section">
            <h2>🚨 Vulnérabilités Critiques</h2>
            <p>Ces vulnérabilités permettent un accès non autorisé immédiat à l'application.</p>

            <div class="vulnerability-grid">
    """

    # Ajouter les vulnérabilités critiques
    for vuln in vulnerabilities['critical']:
        html_content += f"""
                <div class="vuln-card critical">
                    <span class="severity-badge critical">Critique</span>
                    <h3>{vuln['test']}</h3>
                    <div class="details">{vuln['details']}</div>
                    <div class="code-example">
                        <pre>Payload utilisé: {vuln['test'].split(' - ')[-1] if ' - ' in vuln['test'] else 'N/A'}</pre>
                    </div>
                </div>
        """

    html_content += """
            </div>

            <div class="recommendations">
                <h3>Actions Immédiates Requises</h3>
                <ul>
                    <li>Implémenter des requêtes préparées (prepared statements) pour toutes les requêtes SQL</li>
                    <li>Valider et échapper toutes les entrées utilisateur côté serveur</li>
                    <li>Utiliser une whitelist pour les caractères autorisés dans les champs de connexion</li>
                    <li>Implémenter une normalisation des entrées (trim, lowercase) avant comparaison</li>
                </ul>
            </div>
        </div>

        <div class="section">
            <h2>⚠️ Vulnérabilités Élevées</h2>
            <div class="vulnerability-grid">
    """

    # Ajouter les vulnérabilités élevées
    for vuln in vulnerabilities['high']:
        html_content += f"""
                <div class="vuln-card high">
                    <span class="severity-badge high">Élevé</span>
                    <h3>{vuln['test']}</h3>
                    <div class="details">{vuln['details']}</div>
                </div>
        """

    html_content += """
            </div>
        </div>

        <div class="section">
            <h2>📊 Détails des Tests</h2>
            <div class="test-results">
    """

    # Ajouter tous les résultats de tests
    for test in data['test_results']:
        status_class = 'passed' if test['passed'] else 'failed'
        status_icon = '✅' if test['passed'] else '❌'

        html_content += f"""
                <div class="test-item {status_class}">
                    <span class="status">{status_icon}</span>
                    <div>
                        <div class="name">{test['test']}</div>
                        {'<div class="details">' + test['details'] + '</div>' if test['details'] else ''}
                    </div>
                </div>
        """

    html_content += """
            </div>
        </div>

        <div class="section">
            <h2>🛡️ Recommandations de Sécurité</h2>

            <h3>1. Protection contre les Injections SQL</h3>
            <div class="code-example">
                <pre>// ❌ Mauvaise pratique
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;

// ✅ Bonne pratique - Utiliser des paramètres liés
const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
db.query(query, [username, hashedPassword]);</pre>
            </div>

            <h3>2. Validation des Entrées</h3>
            <div class="code-example">
                <pre>// Backend - Validation stricte
function validateUsername(username) {
    // Supprimer les espaces
    username = username.trim();

    // Convertir en minuscules pour éviter la confusion de casse
    username = username.toLowerCase();

    // Vérifier le format (alphanumeric uniquement)
    if (!/^[a-z0-9]+$/.test(username)) {
        throw new Error('Format de nom d\'utilisateur invalide');
    }

    return username;
}</pre>
            </div>

            <h3>3. Limitation des Tentatives</h3>
            <div class="code-example">
                <pre>// Express Rate Limiting
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 tentatives maximum
    message: 'Trop de tentatives de connexion, veuillez réessayer plus tard'
});

app.post('/api/auth/signin', loginLimiter, authController);</pre>
            </div>

            <h3>4. Logging et Monitoring</h3>
            <ul>
                <li>Logger toutes les tentatives de connexion échouées avec l'IP source</li>
                <li>Alerter sur les patterns d'attaque (multiples échecs, caractères suspects)</li>
                <li>Implémenter un système de détection d'intrusion (IDS)</li>
            </ul>
        </div>

        <div class="section">
            <h2>📈 Plan d'Action</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f3f4f6;">
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Priorité</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Action</th>
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Délai</th>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        <span class="severity-badge critical">Critique</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        Corriger les injections SQL permettant le bypass d'authentification
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">Immédiat</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        <span class="severity-badge high">Élevé</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        Implémenter la normalisation des entrées (trim, lowercase)
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">24h</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        <span class="severity-badge high">Élevé</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        Ajouter un système de rate limiting
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">48h</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        <span class="severity-badge medium">Moyen</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">
                        Mettre en place un système de logging complet
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e5e7eb;">1 semaine</td>
                </tr>
            </table>
        </div>

        <div class="footer">
            <p>Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}</p>
            <p>Tests effectués avec Selenium WebDriver | Standards OWASP Top 10</p>
        </div>
    </div>
</body>
</html>
    """

    # Sauvegarder le rapport HTML
    output_file = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Rapport HTML généré: {output_file}")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        json_files = list(Path('.').glob('security_report_*.json'))
        if json_files:
            json_file = sorted(json_files)[-1]
        else:
            print("❌ Aucun fichier JSON trouvé")
            sys.exit(1)

    generate_html_report(json_file)
