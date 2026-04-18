# KaliAgent Integration Guides

Integrate KaliAgent with your existing security tools and workflows.

---

## Table of Contents

1. [SIEM Integration](#siem-integration)
2. [Ticketing Systems](#ticketing-systems)
3. [Slack/Teams Notifications](#slackteams-notifications)
4. [Email Integration](#email-integration)
5. [Vulnerability Scanners](#vulnerability-scanners)
6. [Threat Intelligence](#threat-intelligence)
7. [SOAR Platforms](#soar-platforms)
8. [Custom Webhooks](#custom-webhooks)
9. [API Client Examples](#api-client-examples)
10. [Best Practices](#best-practices)

---

## SIEM Integration

### Splunk

#### Forward Audit Logs to Splunk

**Step 1: Configure Universal Forwarder**

```bash
# /opt/splunkforwarder/etc/system/local/inputs.conf
[monitor:///var/log/kali/audit.jsonl]
disabled = false
index = security
sourcetype = kali:audit
host = kali-agent-server
```

**Step 2: Create Splunk Props**

```ini
# /opt/splunk/etc/system/local/props.conf
[kali:audit]
TIME_FORMAT = %Y-%m-%dT%H:%M:%S.%3NZ
TIME_PREFIX = "timestamp":\s*"
MAX_TIMESTAMP_LOOKAHEAD = 32
SHOULD_LINEMERGE = false
LINE_BREAKER = ([\r\n]+)
```

**Step 3: Create Splunk Search**

```spl
# Real-time security monitoring
index=security sourcetype=kali:audit
| stats count by tool_name, target, user
| where count > 10
| alert
```

**Step 4: Create Dashboard**

```xml
<!-- Save as $SPLUNK_HOME/etc/apps/search/local/data/ui/nav/search.xml -->
<nav>
  <collection label="KaliAgent">
    <view name="kali_agent_overview"/>
    <view name="kali_agent_findings"/>
    <view name="kali_agent_users"/>
  </collection>
</nav>
```

#### Automated Alert: Critical Finding Detected

```spl
index=security sourcetype=kali:audit 
| spath 
| search findings.severity="critical"
| sendalert email.to=security-team@example.com
```

---

### ELK Stack (Elasticsearch, Logstash, Kibana)

#### Logstash Configuration

```conf
# /etc/logstash/conf.d/kali.conf
input {
  file {
    path => "/var/log/kali/audit.jsonl"
    codec => json
    type => "kali-audit"
    start_position => "beginning"
  }
}

filter {
  if [type] == "kali-audit" {
    date {
      match => [ "timestamp", "ISO8601" ]
      target => "@timestamp"
    }
    
    if [tool_name] {
      mutate {
        add_tag => ["kali", "security", "pentesting"]
      }
    }
    
    if [findings] {
      foreach => "findings" {
        if "[findings][severity]" == "critical" {
          mutate {
            add_tag => ["critical_finding"]
          }
        }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "kali-audit-%{+YYYY.MM.dd}"
  }
  
  if "critical_finding" in [tags] {
    email {
      to => "security-team@example.com"
      subject => "CRITICAL Finding Detected: %{tool_name}"
      body => "Critical finding from %{tool_name} on %{target}"
    }
  }
}
```

#### Kibana Dashboard

**Import Dashboard:**
```bash
curl -X POST "localhost:5601/api/saved_objects/_import" \
  -H "kbn-xsrf: true" \
  --form file=@kali_dashboard.ndjson
```

**Dashboard Includes:**
- Audit log timeline
- Tool execution count
- Findings by severity
- User activity heatmap
- Target distribution map

---

### QRadar

#### Step 1: Create Log Source

```bash
# SSH to QRadar console
/opt/qradar/bin/logsource.sh create \
  --name "KaliAgent" \
  --type_name "Generic Device" \
  --description "KaliAgent Security Automation" \
  --protocol "Syslog" \
  --identifier "kali-agent"
```

#### Step 2: Configure Syslog Forwarding

```bash
# /etc/rsyslog.d/kali.conf
if $programname == 'kali-agent' then @qradar-server:514
```

#### Step 3: Create QRadar Rule

```xml
<!-- Rule: Critical Finding Detection -->
<rule>
  <name>KaliAgent - Critical Finding</name>
  <description>Detect critical findings from KaliAgent</description>
  <enabled>true</enabled>
  <criteria>
    <expression>
      <field>eventcategory</field>
      <operator>EQ</operator>
      <value>pentesting</value>
    </expression>
    <expression>
      <field>severity</field>
      <operator>EQ</operator>
      <value>critical</value>
    </expression>
  </criteria>
  <response>
    <email>security-team@example.com</email>
    <ticket>Create Incident</ticket>
  </response>
</rule>
```

---

## Ticketing Systems

### Jira Integration

#### Create Jira Issues from Findings

```python
#!/usr/bin/env python3
"""
Jira Integration for KaliAgent
Automatically create Jira tickets for findings
"""

from jira import JIRA
import requests

class KaliJiraIntegration:
    def __init__(self, jira_url, username, api_token):
        self.jira = JIRA(
            server=jira_url,
            basic_auth=(username, api_token)
        )
    
    def create_ticket_from_finding(self, finding, engagement_id):
        """Create Jira ticket for a finding"""
        
        # Map severity to Jira priority
        priority_map = {
            'critical': 'Highest',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low',
            'informational': 'Lowest'
        }
        
        issue_dict = {
            'project': {'key': 'SEC'},
            'summary': f"[KaliAgent] {finding['title']}",
            'description': f"""
h2. Finding Details

*Severity:* {finding['severity']}
*Target:* {finding.get('target', 'N/A')}
*Tool:* {finding.get('tool', 'N/A')}

h2. Description

{finding['description']}

h2. Evidence

{finding.get('evidence', 'No evidence provided')}

h2. Remediation

{finding.get('remediation', 'No remediation provided')}

h2. Engagement

Engagement ID: {engagement_id}
            """,
            'issuetype': {'name': 'Security Issue'},
            'priority': {'name': priority_map.get(finding['severity'], 'Medium')},
            'labels': ['kali-agent', 'security', 'pentesting'],
        }
        
        new_issue = self.jira.create_issue(fields=issue_dict)
        
        # Attach report if available
        if 'report_url' in finding:
            self.jira.add_attachment(
                issue=new_issue,
                attachment=finding['report_url']
            )
        
        return new_issue.key
    
    def bulk_create_tickets(self, findings, engagement_id):
        """Create tickets for multiple findings"""
        tickets = []
        for finding in findings:
            ticket_key = self.create_ticket_from_finding(finding, engagement_id)
            tickets.append(ticket_key)
            print(f"Created ticket {ticket_key} for {finding['title']}")
        return tickets

# Usage
if __name__ == "__main__":
    jira = KaliJiraIntegration(
        jira_url="https://your-company.atlassian.net",
        username="your-email@example.com",
        api_token="your-api-token"
    )
    
    # Get findings from KaliAgent API
    response = requests.get(
        "http://localhost:8001/api/engagements/eng-001/results"
    )
    findings = response.json().get('findings', [])
    
    # Create tickets
    tickets = jira.bulk_create_tickets(findings, "eng-001")
    print(f"Created {len(tickets)} tickets")
```

#### Jira Workflow Configuration

```xml
<!-- Add to workflow descriptor -->
<workflow name="Security Finding Workflow">
  <statuses>
    <status id="1" name="Open"/>
    <status id="2" name="In Progress"/>
    <status id="3" name="Remediated"/>
    <status id="4" name="Verified"/>
    <status id="5" name="Closed"/>
  </statuses>
  <transitions>
    <transition id="11" name="Start Work"/>
    <transition id="21" name="Mark Remediated"/>
    <transition id="31" name="Verify Fix"/>
    <transition id="41" name="Close"/>
  </transitions>
</workflow>
```

---

### ServiceNow Integration

#### Create Incident from Finding

```python
#!/usr/bin/env python3
"""
ServiceNow Integration for KaliAgent
"""

import requests
from requests.auth import HTTPBasicAuth

class KaliServiceNowIntegration:
    def __init__(self, instance, username, password):
        self.instance = instance
        self.auth = HTTPBasicAuth(username, password)
        self.base_url = f"https://{instance}.service-now.com/api/now/table"
    
    def create_incident(self, finding, engagement_id):
        """Create ServiceNow incident"""
        
        # Map severity
        urgency_map = {
            'critical': '1',
            'high': '2',
            'medium': '3',
            'low': '4'
        }
        
        incident_data = {
            'short_description': f"[KaliAgent] {finding['title']}",
            'description': f"""
Finding Details:
- Severity: {finding['severity']}
- Target: {finding.get('target', 'N/A')}
- Tool: {finding.get('tool', 'N/A')}

Description:
{finding['description']}

Remediation:
{finding.get('remediation', 'N/A')}

Engagement: {engagement_id}
            """,
            'urgency': urgency_map.get(finding['severity'], '3'),
            'impact': '2',
            'category': 'Security',
            'subcategory': 'Vulnerability Management',
            'u_engagement_id': engagement_id,
            'u_finding_severity': finding['severity'],
        }
        
        response = requests.post(
            f"{self.base_url}/incident",
            auth=self.auth,
            json=incident_data,
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        return result['result']['number']
    
    def update_incident(self, incident_number, updates):
        """Update existing incident"""
        response = requests.patch(
            f"{self.base_url}/incident?number={incident_number}",
            auth=self.auth,
            json=updates,
            headers={'Content-Type': 'application/json'}
        )
        return response.json()

# Usage
if __name__ == "__main__":
    snow = KaliServiceNowIntegration(
        instance="your-instance",
        username="integration-user",
        password="password"
    )
    
    finding = {
        'title': 'SQL Injection Vulnerability',
        'severity': 'critical',
        'target': 'app.example.com',
        'tool': 'SQLMap',
        'description': 'SQL injection found in login form',
        'remediation': 'Use parameterized queries'
    }
    
    incident = snow.create_incident(finding, "eng-001")
    print(f"Created incident: {incident}")
```

---

## Slack/Teams Notifications

### Slack Integration

#### Real-time Notifications

```python
#!/usr/bin/env python3
"""
Slack Integration for KaliAgent
"""

import requests
import json

class KaliSlackIntegration:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_notification(self, message, attachments=None, channel=None):
        """Send notification to Slack"""
        
        payload = {
            'text': message,
            'attachments': attachments or [],
        }
        
        if channel:
            payload['channel'] = channel
        
        response = requests.post(
            self.webhook_url,
            json=payload
        )
        
        return response.status_code == 200
    
    def send_finding_alert(self, finding, engagement_id):
        """Send alert for critical finding"""
        
        # Color by severity
        color_map = {
            'critical': 'danger',
            'high': 'warning',
            'medium': '#3b82f6',
            'low': 'good',
            'informational': '#6b7280'
        }
        
        attachments = [{
            'color': color_map.get(finding['severity'], '#6b7280'),
            'title': f"🚨 {finding['severity'].upper()} Finding Detected",
            'fields': [
                {
                    'title': 'Finding',
                    'value': finding['title'],
                    'short': False
                },
                {
                    'title': 'Target',
                    'value': finding.get('target', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Tool',
                    'value': finding.get('tool', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Engagement',
                    'value': engagement_id,
                    'short': True
                }
            ],
            'footer': 'KaliAgent Security Automation',
            'footer_icon': 'https://example.com/logo.png'
        }]
        
        message = f"Critical security finding detected in engagement {engagement_id}"
        
        return self.send_notification(
            message,
            attachments,
            channel='#security-alerts'
        )
    
    def send_engagement_complete(self, engagement_id, stats):
        """Send engagement completion notification"""
        
        attachments = [{
            'color': 'good',
            'title': '✅ Engagement Complete',
            'fields': [
                {
                    'title': 'Engagement ID',
                    'value': engagement_id,
                    'short': True
                },
                {
                    'title': 'Tools Executed',
                    'value': str(stats['tools_executed']),
                    'short': True
                },
                {
                    'title': 'Findings',
                    'value': str(stats['findings']),
                    'short': True
                },
                {
                    'title': 'Duration',
                    'value': stats['duration'],
                    'short': True
                }
            ]
        }]
        
        message = f"Security engagement {engagement_id} completed successfully"
        
        return self.send_notification(
            message,
            attachments,
            channel='#security-reports'
        )

# Usage in KaliAgent server.py
slack = KaliSlackIntegration(webhook_url="https://hooks.slack.com/services/...")

# Send alert for critical finding
if finding['severity'] == 'critical':
    slack.send_finding_alert(finding, engagement_id)
```

#### Slack App Manifest

```yaml
# slack-app-manifest.yaml
display_information:
  name: KaliAgent
  description: Security Automation Notifications
  background_color: "#0f172a"

features:
  bot_user:
    display_name: KaliAgent Bot
    always_online: true

oauth_config:
  scopes:
    bot:
      - chat:write
      - channels:read
      - incoming-webhook

settings:
  event_subscriptions:
    bot_events:
      - type: message.channels
  interactivity:
    is_enabled: true
  socket_mode_enabled: false
```

---

### Microsoft Teams Integration

```python
#!/usr/bin/env python3
"""
Microsoft Teams Integration for KaliAgent
"""

import requests
from datetime import datetime

class KaliTeamsIntegration:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_card(self, title, text, facts=None, color=None):
        """Send adaptive card to Teams"""
        
        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color or "0076D7",
            "summary": title,
            "sections": [{
                "activityTitle": title,
                "activitySubtitle": "KaliAgent Security Automation",
                "activityImage": "https://example.com/logo.png",
                "facts": facts or [],
                "text": text
            }]
        }
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.status_code == 200
    
    def send_finding_alert(self, finding, engagement_id):
        """Send finding alert to Teams"""
        
        color_map = {
            'critical': 'FF0000',
            'high': 'FFA500',
            'medium': '0080FF',
            'low': '008000'
        }
        
        facts = [
            {'name': 'Severity', 'value': finding['severity'].upper()},
            {'name': 'Target', 'value': finding.get('target', 'N/A')},
            {'name': 'Tool', 'value': finding.get('tool', 'N/A')},
            {'name': 'Engagement', 'value': engagement_id}
        ]
        
        return self.send_card(
            title=f"🚨 {finding['severity'].upper()} Finding Detected",
            text=finding['description'],
            facts=facts,
            color=color_map.get(finding['severity'], '808080')
        )

# Usage
teams = KaliTeamsIntegration(
    webhook_url="https://outlook.office.com/webhook/..."
)

teams.send_finding_alert(finding, "eng-001")
```

---

## Email Integration

### SMTP Configuration

```python
#!/usr/bin/env python3
"""
Email Integration for KaliAgent
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class KaliEmailIntegration:
    def __init__(self, smtp_host, smtp_port, username, password, from_email):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    def send_report(self, to_emails, subject, body, attachment_path=None):
        """Send email with optional attachment"""
        
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        if attachment_path:
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={attachment_path.split("/")[-1]}'
                )
                msg.attach(part)
        
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        server.send_message(msg)
        server.quit()
        
        return True
    
    def send_finding_alert(self, to_emails, finding, engagement_id):
        """Send email alert for critical finding"""
        
        subject = f"[CRITICAL] {finding['title']} - {engagement_id}"
        
        body = f"""
        <html>
        <body>
            <h2 style="color: red;">🚨 Critical Security Finding</h2>
            
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Finding:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{finding['title']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Severity:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: red;">{finding['severity'].upper()}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Target:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{finding.get('target', 'N/A')}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Description:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{finding['description']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Remediation:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{finding.get('remediation', 'N/A')}</td>
                </tr>
            </table>
            
            <p>Engagement: {engagement_id}</p>
            <p><em>Generated by KaliAgent Security Automation</em></p>
        </body>
        </html>
        """
        
        return self.send_report(to_emails, subject, body)

# Usage
email = KaliEmailIntegration(
    smtp_host='smtp.example.com',
    smtp_port=587,
    username='kali-agent@example.com',
    password='password',
    from_email='kali-agent@example.com'
)

email.send_finding_alert(
    to_emails=['security-team@example.com'],
    finding=finding,
    engagement_id='eng-001'
)
```

---

## Vulnerability Scanners

### Nessus Integration

```python
#!/usr/bin/env python3
"""
Nessus Integration for KaliAgent
Import findings from Nessus scans
"""

import requests

class KaliNessusIntegration:
    def __init__(self, nessus_url, access_key, secret_key):
        self.nessus_url = nessus_url
        self.headers = {
            'X-ApiKeys': f'accessKey={access_key}; secretKey={secret_key}',
            'Content-Type': 'application/json'
        }
    
    def get_scan_results(self, scan_id):
        """Get results from Nessus scan"""
        
        # Export scan results
        export_response = requests.post(
            f"{self.nessus_url}/scans/{scan_id}/export",
            headers=self.headers,
            json={'format': 'json'}
        )
        
        file_id = export_response.json()['file']
        
        # Download results
        download_response = requests.get(
            f"{self.nessus_url}/scans/{scan_id}/export/{file_id}/download",
            headers=self.headers
        )
        
        return download_response.json()
    
    def import_to_kaliagent(self, scan_results, engagement_id):
        """Import Nessus findings to KaliAgent"""
        
        findings = []
        
        for vulnerability in scan_results.get('vulnerabilities', []):
            finding = {
                'title': vulnerability['plugin_name'],
                'severity': self._map_severity(vulnerability['severity']),
                'description': vulnerability['description'],
                'remediation': vulnerability.get('solution', 'N/A'),
                'tool': 'Nessus',
                'target': vulnerability.get('host', {}).get('hostname', 'N/A'),
                'evidence': vulnerability.get('output', '')
            }
            findings.append(finding)
        
        # Add to KaliAgent engagement
        requests.post(
            f"http://localhost:8001/api/engagements/{engagement_id}/findings",
            json={'findings': findings}
        )
        
        return len(findings)
    
    def _map_severity(self, nessus_severity):
        """Map Nessus severity to KaliAgent severity"""
        mapping = {
            0: 'informational',
            1: 'low',
            2: 'medium',
            3: 'high',
            4: 'critical'
        }
        return mapping.get(nessus_severity, 'medium')

# Usage
nessus = KaliNessusIntegration(
    nessus_url='https://nessus.example.com',
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY'
)

scan_results = nessus.get_scan_results(scan_id=123)
count = nessus.import_to_kaliagent(scan_results, 'eng-001')
print(f"Imported {count} findings from Nessus")
```

---

## Threat Intelligence

### VirusTotal Integration

```python
#!/usr/bin/env python3
"""
VirusTotal Integration for KaliAgent
Enrich findings with threat intelligence
"""

import requests

class KaliVirusTotalIntegration:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://www.virustotal.com/api/v3'
        self.headers = {
            'x-apikey': api_key
        }
    
    def check_hash(self, file_hash):
        """Check file hash against VirusTotal"""
        
        response = requests.get(
            f"{self.base_url}/files/{file_hash}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            return {
                'detections': data['last_analysis_stats']['malicious'],
                'total': sum(data['last_analysis_stats'].values()),
                'permalink': data['links']['self'],
                'first_seen': data['first_submission_date'],
                'tags': data.get('tags', [])
            }
        
        return None
    
    def check_domain(self, domain):
        """Check domain reputation"""
        
        response = requests.get(
            f"{self.base_url}/domains/{domain}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()['data']
            return {
                'detections': data['last_analysis_stats']['malicious'],
                'categories': data.get('categories', {}),
                'reputation': data.get('reputation', 0)
            }
        
        return None
    
    def enrich_finding(self, finding):
        """Enrich finding with threat intelligence"""
        
        if 'hash' in finding:
            vt_data = self.check_hash(finding['hash'])
            if vt_data:
                finding['threat_intel'] = {
                    'source': 'VirusTotal',
                    'detections': f"{vt_data['detections']}/{vt_data['total']}",
                    'permalink': vt_data['permalink']
                }
        
        if 'domain' in finding:
            vt_data = self.check_domain(finding['domain'])
            if vt_data:
                finding['threat_intel'] = {
                    'source': 'VirusTotal',
                    'detections': f"{vt_data['detections']} malicious vendors",
                    'reputation': vt_data['reputation']
                }
        
        return finding

# Usage
vt = KaliVirusTotalIntegration(api_key='YOUR_API_KEY')

finding = {
    'title': 'Malware Detected',
    'hash': 'd41d8cd98f00b204e9800998ecf8427e',
    'severity': 'critical'
}

enriched = vt.enrich_finding(finding)
print(f"VirusTotal detections: {enriched.get('threat_intel', {})}")
```

---

## SOAR Platforms

### Palo Alto Cortex XSOAR

```python
#!/usr/bin/env python3
"""
Cortex XSOAR Integration for KaliAgent
"""

import demisto

def create_xsoar_incident(finding, engagement_id):
    """Create XSOAR incident from finding"""
    
    incident = {
        'name': f"KaliAgent: {finding['title']}",
        'type': 'Security Finding',
        'severity': map_severity_to_xsoar(finding['severity']),
        'owner': 'SOC Team',
        'details': finding['description'],
        'occurred': finding.get('timestamp', ''),
        'customFields': {
            'kaliengagementid': engagement_id,
            'kalitool': finding.get('tool', ''),
            'kalitarget': finding.get('target', ''),
            'kalifindingseverity': finding['severity']
        }
    }
    
    demisto.createIncident(incident)
    
    return incident['name']

def map_severity_to_xsoar(severity):
    """Map KaliAgent severity to XSOAR severity"""
    mapping = {
        'critical': 4,  # Critical
        'high': 3,      # High
        'medium': 2,    # Medium
        'low': 1,       # Low
        'informational': 0  # Informational
    }
    return mapping.get(severity, 2)

# XSOAR Automation Script
if __name__ == '__main__':
    finding = demisto.args().get('finding')
    engagement_id = demisto.args().get('engagement_id')
    
    incident_name = create_xsoar_incident(finding, engagement_id)
    demisto.results(f"Created XSOAR incident: {incident_name}")
```

---

## Custom Webhooks

### Webhook Configuration

```python
#!/usr/bin/env python3
"""
Custom Webhook Integration for KaliAgent
"""

import requests
import hashlib
import hmac
import json
from datetime import datetime

class KaliWebhookIntegration:
    def __init__(self, webhook_url, secret=None):
        self.webhook_url = webhook_url
        self.secret = secret
    
    def send_event(self, event_type, data):
        """Send webhook event"""
        
        payload = {
            'event': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Add signature if secret is configured
        if self.secret:
            signature = hmac.new(
                self.secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-KaliAgent-Signature'] = signature
        
        response = requests.post(
            self.webhook_url,
            json=payload,
            headers=headers
        )
        
        return response.status_code == 200
    
    def send_finding_created(self, finding, engagement_id):
        """Webhook: Finding created"""
        return self.send_event('finding.created', {
            'finding': finding,
            'engagement_id': engagement_id
        })
    
    def send_engagement_started(self, engagement):
        """Webhook: Engagement started"""
        return self.send_event('engagement.started', {
            'engagement': engagement
        })
    
    def send_engagement_completed(self, engagement, stats):
        """Webhook: Engagement completed"""
        return self.send_event('engagement.completed', {
            'engagement': engagement,
            'statistics': stats
        })

# Usage
webhook = KaliWebhookIntegration(
    webhook_url='https://your-system.com/webhooks/kaliagent',
    secret='your-webhook-secret'
)

# Send event
webhook.send_finding_created(finding, 'eng-001')
```

---

## API Client Examples

### Python Client

```python
#!/usr/bin/env python3
"""
KaliAgent Python Client Library
"""

import requests
from typing import List, Dict, Optional

class KaliAgentClient:
    def __init__(self, base_url: str = "http://localhost:8001", api_key: Optional[str] = None):
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.headers['Authorization'] = f"Bearer {api_key}"
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        return response.json()
    
    def create_engagement(self, name: str, engagement_type: str, targets: List[str]) -> Dict:
        """Create new engagement"""
        response = self.session.post(
            f"{self.base_url}/api/engagements",
            json={
                'name': name,
                'engagement_type': engagement_type,
                'targets': targets
            }
        )
        return response.json()
    
    def execute_playbook(self, engagement_id: str, playbook_type: str, **kwargs) -> Dict:
        """Execute playbook"""
        response = self.session.post(
            f"{self.base_url}/api/engagements/{engagement_id}/playbook",
            json={
                'playbook_type': playbook_type,
                **kwargs
            }
        )
        return response.json()
    
    def get_results(self, engagement_id: str) -> Dict:
        """Get engagement results"""
        response = self.session.get(
            f"{self.base_url}/api/engagements/{engagement_id}/results"
        )
        return response.json()
    
    def generate_report(self, engagement_id: str, format: str = "pdf") -> bytes:
        """Generate report"""
        response = self.session.get(
            f"{self.base_url}/api/engagements/{engagement_id}/report",
            params={'format': format}
        )
        return response.content
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """List available tools"""
        params = {'category': category} if category else {}
        response = self.session.get(
            f"{self.base_url}/api/tools",
            params=params
        )
        return response.json()['tools']

# Usage
if __name__ == "__main__":
    client = KaliAgentClient()
    
    # Health check
    health = client.health_check()
    print(f"Status: {health['status']}")
    
    # Create engagement
    engagement = client.create_engagement(
        name="Test Engagement",
        engagement_type="reconnaissance",
        targets=["scanme.nmap.org"]
    )
    print(f"Created: {engagement['engagement_id']}")
    
    # Execute playbook
    result = client.execute_playbook(
        engagement['engagement_id'],
        playbook_type="recon",
        target="scanme.nmap.org"
    )
    print(f"Executed {len(result['tools_executed'])} tools")
    
    # Get results
    results = client.get_results(engagement['engagement_id'])
    print(f"Found {len(results.get('findings', []))} findings")
    
    # Generate report
    report = client.generate_report(engagement['engagement_id'], format="pdf")
    with open("report.pdf", "wb") as f:
        f.write(report)
    print("Report saved to report.pdf")
```

---

## Best Practices

### Security

1. **Use API Keys**: Always authenticate API requests
2. **Encrypt Secrets**: Store credentials in vault (HashiCorp Vault, AWS Secrets Manager)
3. **HTTPS Only**: Use TLS for all integrations
4. **Webhook Signatures**: Verify webhook authenticity
5. **Rate Limiting**: Implement rate limits to prevent abuse

### Reliability

1. **Retry Logic**: Implement exponential backoff for failed requests
2. **Circuit Breakers**: Prevent cascade failures
3. **Dead Letter Queues**: Store failed events for later processing
4. **Health Checks**: Monitor integration health
5. **Alerting**: Set up alerts for integration failures

### Performance

1. **Async Processing**: Use async for non-blocking operations
2. **Batching**: Batch multiple events together
3. **Caching**: Cache frequently accessed data
4. **Connection Pooling**: Reuse HTTP connections
5. **Compression**: Use gzip for large payloads

### Monitoring

1. **Metrics**: Track success rates, latencies, error rates
2. **Logging**: Log all integration events
3. **Tracing**: Use distributed tracing for complex workflows
4. **Dashboards**: Create monitoring dashboards
5. **Alerts**: Set up proactive alerts

---

*Last Updated: April 18, 2026*
*Version: 1.0.0*
