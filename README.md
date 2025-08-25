# WHOOP Copilot

Combine WHOOP fitness data with Copilot Money financial data for insights into health-finance correlations.

## Features

- 🔐 WHOOP OAuth authentication with PKCE
- 💰 Copilot Money API integration
- 📊 Data analysis and correlation insights
- 🎯 CLI interface with rich output
- 📈 Recovery vs spending analysis
- 💪 Workout impact on spending patterns

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   Create a `.env` file with:
   ```
   WHOOP_CLIENT_ID=your_whoop_client_id
   WHOOP_CLIENT_SECRET=your_whoop_client_secret
   COPILOT_API_KEY=your_copilot_api_key
   ```

3. **Install the package:**
   ```bash
   pip install -e .
   ```

## Usage

### Authentication
```bash
whoop-copilot auth
```

### Check WHOOP Status
```bash
whoop-copilot whoop-status --days 30
```

### Check Copilot Money Status
```bash
whoop-copilot copilot-status --days 30
```

### Analyze Correlations
```bash
whoop-copilot analyze --days 30 --output report.json
```

### Quick Insights
```bash
whoop-copilot quick-insights --days 7
```

## API Endpoints

- **WHOOP**: Sleep, recovery, workouts, cycles
- **Copilot Money**: Transactions, accounts, insights

## Data Analysis

- Recovery score vs daily spending correlation
- Workout day vs non-workout day spending patterns
- Comprehensive health-finance reports
