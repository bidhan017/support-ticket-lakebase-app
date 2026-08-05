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
* **Database**: PostgreSQL (Lakebase)
* **Hosting**: Databricks Apps
* **Security**: Databricks Secrets for credential management

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
1. Create a Databricks secret scope `support-app-secrets`
2. Prompt you for your PostgreSQL connection string
3. Store it securely in Databricks Secrets
4. Set appropriate permissions

#### Option B: Manual Setup

Using the Databricks CLI:

```bash
# Create secret scope
databricks secrets create-scope support-app-secrets

# Store connection string
databricks secrets put-secret support-app-secrets database-url \
  --string-value "postgresql://username:password@host:port/database?sslmode=require"

# Set permissions
databricks secrets put-acl support-app-secrets users READ
```

### 4. Configuration

The `app.yaml` file is already configured to reference the secret:

```yaml
env:
  - name: DATABASE_URL
    value: "{{secrets/support-app-secrets/database-url}}"
```

**✅ Safe to commit** - This references the secret without exposing credentials.

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
├── app.yaml               # Databricks Apps configuration
├── requirements.txt       # Python dependencies
├── setup_secrets.py       # Secret management script (run once)
├── .gitignore            # Prevents committing sensitive files
├── README.md             # This file
└── LICENSE               # License file
```

## Security Best Practices

### ✅ DO:

* Store credentials in Databricks Secrets
* Reference secrets using `{{secrets/scope/key}}` syntax in `app.yaml`
* Use `.gitignore` to prevent committing sensitive files
* Rotate credentials regularly
* Use read-only database users when possible

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

# Set environment variable
export DATABASE_URL="postgresql://..."

# Run locally
streamlit run app.py
```

### Adding Features

1. Update `app.py` with your changes
2. Test locally
3. Commit and push to GitHub
4. App will auto-deploy

## Troubleshooting

### "Missing DATABASE_URL environment variable"

**Cause**: Secret not configured or app doesn't have access.

**Fix**:
1. Run `setup_secrets.py` to configure the secret
2. Verify secret exists: `databricks secrets list-secrets support-app-secrets`
3. Check app has read access to the scope

### Connection errors

**Cause**: Database unreachable or credentials incorrect.

**Fix**:
1. Test connection string manually: `psql "postgresql://..."`
2. Verify database allows connections from Databricks IPs
3. Check SSL mode is set correctly (`?sslmode=require`)

### App deployment fails

**Cause**: Invalid `app.yaml` or missing files.

**Fix**:
1. Validate YAML syntax
2. Ensure all files are committed to Git
3. Check app logs: `databricks apps logs support-ticket-lakebase-app`

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
