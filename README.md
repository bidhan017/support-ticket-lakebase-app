# Support Ticket Application

A Databricks App for managing internal support tickets, built with Streamlit and backed by PostgreSQL (Lakebase).

## Features

* 📋 View and filter support tickets by status (Open, In Progress, Resolved)
* 💬 View ticket messages and conversation history
* ✨ Create new tickets
* 📝 Add messages to existing tickets
* 🔄 Update ticket status
* 📊 Real-time statistics dashboard

## Architecture

* **Frontend**: Streamlit
* **Database**: PostgreSQL (Lakebase or external)
* **Hosting**: Databricks Apps
* **Security**: Databricks Secrets for credential management
* **Authentication**: Databricks SDK with runtime secret fetching

## How It Works

1. **Secret Storage**: Database connection string is stored in Databricks Secrets (scope: `database`, key: `lakebase-url`)
2. **Runtime Retrieval**: App uses Databricks SDK to fetch the secret when connecting to the database
3. **Base64 Decoding**: Databricks Secrets API returns base64-encoded values - the app decodes them automatically
4. **Connection**: psycopg2 uses the decoded connection string to connect to PostgreSQL

```python
# Simplified connection flow in app.py
import base64
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
secret_value = w.secrets.get_secret(scope="database", key="lakebase-url").value
connection_string = base64.b64decode(secret_value).decode('utf-8')
conn = psycopg2.connect(connection_string)
```

## Setup Instructions

### 1. Prerequisites

* Databricks workspace access
* PostgreSQL database (Lakebase or external)
* GitHub repository (for Git-backed deployment)

### 2. Database Setup

Your database should have the following schema:

```sql
-- Tickets table
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ticket messages table
CREATE TABLE ticket_messages (
    message_id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticket_messages_ticket_id ON ticket_messages(ticket_id);
```

### 3. Secure Credential Setup

**IMPORTANT**: Never commit database credentials to Git!

#### Option A: Run the Setup Script (Recommended)

```bash
python setup_secrets.py
```

The script will:
1. Create a Databricks secret scope `database`
2. Prompt you for your PostgreSQL connection string
3. Store it securely in Databricks Secrets as `lakebase-url`
4. Set appropriate permissions

**Connection String Format:**
```
postgresql://username:password@host:port/database?sslmode=require
```

For example:
```
postgresql://student:npg_xxx@ep-xxx.database.us-east-2.cloud.databricks.com:5432/databricks_postgres?sslmode=require
```

#### Option B: Manual Setup

Using the Databricks CLI:

```bash
# Create secret scope
databricks secrets create-scope database

# Store connection string
databricks secrets put-secret database lakebase-url \
  --string-value "postgresql://username:password@host:port/database?sslmode=require"

# Set permissions
databricks secrets put-acl database users READ
```

### 4. Configuration

The `app.yaml` file is minimal - no environment variables needed:

```yaml
command:
  - "streamlit"
  - "run"
  - "app.py"
```

**How it works**: The app fetches the connection string at runtime using the Databricks SDK:
```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
secret_value = w.secrets.get_secret(scope="database", key="lakebase-url").value
```

**✅ Safe to commit** - No credentials in code or configuration.

### 5. Deploy to Databricks Apps

#### First-time Deployment

```bash
# Install Databricks CLI if needed
pip install databricks-cli

# Configure authentication
databricks configure

# Deploy the app
databricks apps deploy support-ticket-lakebase-app \
  --source-code-path . \
  --git-repository https://github.com/YOUR_USERNAME/support-ticket-lakebase-app
```

#### Updates

Push changes to your Git repository:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

The app will automatically redeploy on the next update.

## File Structure

```
.
├── app.py                 # Main Streamlit application
├── app.yaml               # Databricks Apps configuration (minimal)
├── requirements.txt       # Python dependencies (streamlit, psycopg2-binary, databricks-sdk)
├── setup_secrets.py       # Secret management script (run once)
├── .gitignore            # Prevents committing sensitive files
├── README.md             # This file
└── LICENSE               # License file
```

### Key Dependencies

* `streamlit` - Web framework for the UI
* `psycopg2-binary` - PostgreSQL database adapter
* `databricks-sdk` - Required for fetching secrets at runtime

## Security Best Practices

### ✅ DO:

* Store credentials in Databricks Secrets
* Fetch secrets at runtime using the Databricks SDK
* Use `.gitignore` to prevent committing sensitive files
* Rotate credentials regularly
* Use read-only database users when possible
* Decode base64-encoded secret values properly

### ❌ DON'T:

* Commit passwords or connection strings to Git
* Hardcode credentials in `app.py` or `app.yaml`
* Share credentials in plaintext (Slack, email, etc.)
* Use production credentials in development

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Ensure Databricks CLI is configured
databricks configure

# Set up secrets (run once)
python setup_secrets.py

# Run locally (uses Databricks SDK to fetch secrets)
streamlit run app.py
```

**Note**: Local testing requires:
* Databricks CLI configured with valid credentials
* Secret scope `database` with key `lakebase-url` already set up
* The Databricks SDK will authenticate using your CLI profile

### Adding Features

1. Update `app.py` with your changes
2. Test locally
3. Commit and push to GitHub
4. App will auto-deploy

## Troubleshooting

### "Connection string is empty in secrets"

**Cause**: Secret not configured or app doesn't have access.

**Fix**:
1. Run `setup_secrets.py` to configure the secret
2. Verify secret exists: `databricks secrets list-secrets database`
3. Check app has read access to the scope
4. Verify the secret value is set: `databricks secrets get-secret database lakebase-url`

### Connection errors

**Cause**: Database unreachable or credentials incorrect.

**Fix**:
1. Test connection string manually: `psql "postgresql://..."`
2. Verify database allows connections from Databricks IPs
3. Check SSL mode is set correctly (`?sslmode=require`)

### "invalid dsn: invalid connection option"

**Cause**: Secret value is base64-encoded but not being decoded.

**Fix**:
1. Ensure `app.py` includes base64 decoding:
   ```python
   import base64
   connection_string = base64.b64decode(secret_value).decode('utf-8')
   ```
2. Verify the secret contains a valid connection string (not already base64-encoded)
3. Test decoding manually to verify the format

### App deployment fails

**Cause**: Invalid `app.yaml` or missing files.

**Fix**:
1. Validate YAML syntax
2. Ensure all files are committed to Git
3. Check app logs: `databricks apps logs support-ticket-lakebase-app`
4. Verify all dependencies are listed in `requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Support

For issues or questions:
* Open a GitHub issue
* Contact the development team
* Check Databricks Apps documentation: https://docs.databricks.com/apps/
