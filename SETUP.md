# WHOOP Copilot Setup Guide

## Prerequisites

- Python 3.9 or higher
- WHOOP Developer Account
- Copilot Money API Access

## Installation

1. **Clone and install:**
   ```bash
   git clone <your-repo>
   cd whoop-copilot
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Environment Setup:**
   Create a `.env` file in the project root:
   ```bash
   # WHOOP API Configuration
   WHOOP_CLIENT_ID=your_whoop_client_id_here
   WHOOP_CLIENT_SECRET=your_whoop_client_secret_here
   WHOOP_AUTH_URL=https://api.prod.whoop.com/oauth/oauth2/auth
   WHOOP_TOKEN_URL=https://api.prod.whoop.com/oauth/oauth2/token
   WHOOP_API_URL=https://api.prod.whoop.com/developer
   WHOOP_SCOPES=offline_access read:recovery read:sleep read:cycle read:workout
   
   # Copilot Money API Configuration
   COPILOT_API_KEY=your_copilot_api_key_here
   COPILOT_API_URL=https://api.copilot.money
   
   # Optional: Custom redirect port for OAuth
   REDIRECT_PORT=8765
   ```

## Getting API Credentials

### WHOOP API
1. Go to [WHOOP Developer Portal](https://developer.whoop.com/)
2. Create a new application
3. Note your Client ID and Client Secret
4. Set redirect URI to: `http://127.0.0.1:8765/callback`

### Copilot Money API
1. Contact Copilot Money for API access
2. Get your API key
3. Note the API base URL

## First Run

1. **Authenticate with WHOOP:**
   ```bash
   whoop-copilot auth
   ```
   This will open a browser for OAuth authentication.

2. **Test the setup:**
   ```bash
   whoop-copilot whoop-status --days 7
   whoop-copilot copilot-status --days 7
   ```

## Usage Examples

### Basic Status Checks
```bash
# Check WHOOP data
whoop-copilot whoop-status --days 30

# Check Copilot Money data
whoop-copilot copilot-status --days 30
```

### Analysis
```bash
# Analyze correlations
whoop-copilot analyze --days 30 --output report.json

# Get quick insights
whoop-copilot quick-insights --days 7
```

### Data Export
```bash
# Generate detailed report
whoop-copilot analyze --days 90 --output monthly_report.json
```

## Troubleshooting

### Common Issues

1. **Import errors:** Make sure you've installed with `pip install -e .`
2. **Authentication failures:** Check your `.env` file and WHOOP credentials
3. **API errors:** Verify API keys and endpoints
4. **Port conflicts:** Change `REDIRECT_PORT` in `.env` if 8765 is busy

### Debug Mode
Run with verbose output:
```bash
python -m whoop_copilot.cli --help
```

## Data Privacy

- Tokens are stored locally in `~/.whoop-copilot/tokens.json`
- No data is sent to external servers
- All API calls use secure HTTPS connections
- OAuth flow follows PKCE security standards
