# Management Tools Analysis Dashboard

A comprehensive bilingual analytics dashboard for analyzing management tools adoption and trends across multiple data sources. Built with Dash, Plotly, and Python.

## Features

- **Bilingual Support**: Full Spanish and English language support with automatic browser language detection
- **Multi-Source Data Analysis**: Integrates data from Google Trends, Google Books Ngrams, Crossref, and Bain surveys
- **Temporal Analysis**: 2D and 3D temporal visualizations with customizable time ranges
- **Statistical Analysis**: Correlation heatmaps, regression analysis, PCA, and Fourier analysis
- **Interactive Visualizations**: Dynamic charts with drill-down capabilities
- **Performance Monitoring**: Built-in system performance and database statistics
- **Responsive Design**: Optimized for desktop and mobile devices

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager (recommended)
- Git

### Local Development

```bash
# Clone repository
git clone https://github.com/Wise-Connex/Management-Tools-Analysis.git
cd Management-Tools-Analysis

# Create virtual environment and install dependencies
cd dashboard_app
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Run the application
python app.py

# Access the dashboard
open http://localhost:8050
```

### Bilingual Features

The dashboard automatically detects your browser language:

- 🇪🇸 Spanish users see the interface in Spanish
- 🇬🇧/🇺🇸 English users see the interface in English
- Language can be manually switched using the selector in the sidebar
- Language preference is saved and persists across sessions

## Research Context

This analytical system constitutes an essential component of the research corpus for Diomar Añez's doctoral dissertation, titled _Ontological Dichotomy in "Management Fads"_ (© 2023-2025), conducted under the academic supervision of **Dr. Elizabeth Pereira.**

The research undertakes a critical analysis of the temporal dynamics of management tools, problematizing the practical and discursive phenomenon of "management fads." It empirically examines their life cycle—emergence, diffusion, and eventual persistence or obsolescence—and evaluates their implications for the strategic and structural configuration of contemporary organizations.

The analysis results are relevant to:

- **Executives and Managers**: Informing strategic decisions regarding management tools
- **Academics and Researchers**: Providing empirical basis for organizational dynamics studies
- **Consultants and Advisors**: Offering insights into management tool life cycles

## Tech Stack

### Core Analysis

- Python 3.11+
- Pandas (Data Analysis)
- NumPy (Numerical Computing)
- SciPy (Scientific Computing)
- Statsmodels (Statistical Models)

### Statistical Analysis

- ARIMA (Time Series Modeling)
- Seasonal Decomposition
- Fourier Analysis
- Correlation Analysis

### Dashboard & Visualization

- Dash
- Plotly
- Flask
- Bootstrap

### AI Integration

- Google Gemini API

## Project Structure

```
├── dashboard_app/
│   ├── app.py              # Main dashboard application
│   ├── translations.py      # Bilingual translation system
│   ├── tools.py            # Tool definitions and mappings
│   ├── requirements.txt      # Python dependencies
│   └── data.db            # SQLite database
├── database.py              # Database management
├── Dockerfile              # Container configuration
├── docker-compose.yml       # Local development
├── gunicorn.conf.py        # Production server config
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

## Environment Variables

Create a `.env` file with:

```bash
GOOGLE_API_KEY=your_api_key
```

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for complete configuration options.

## Development

### Running Tests

```bash
cd dashboard_app
python -m pytest
```

### Code Style

Follow PEP 8 guidelines. Use provided .gitignore and .cursorrules.

## Deployment

For production deployment to Dokploy, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bain & Company for management tools data
- Google Books Ngram Viewer
- Crossref.org API
- Google Trends API

## Contact

For questions and support, please open an issue in the repository.
