# AIF360 Enterprise Fairness API

<div align="center">

**Production-grade bias detection system using IBM AI Fairness 360**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![AIF360](https://img.shields.io/badge/AIF360-0.6.1-orange.svg)](https://aif360.readthedocs.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🎯 Overview

Enterprise-grade **fairness analysis API** for AI-driven hiring systems, powered by **IBM AI Fairness 360 (AIF360)**. Detects bias in recruitment decisions and provides actionable recommendations for legal compliance (EEOC, EU AI Act, UK Equality Act).

### Key Features

- ✅ **9+ Fairness Metrics** (Statistical Parity, Disparate Impact, Equal Opportunity, etc.)
- ✅ **AIF360-Powered** (Industry-standard fairness library from IBM Research)
- ✅ **RESTful API** (FastAPI with OpenAPI/Swagger docs)
- ✅ **Production-Ready** (Docker, Gunicorn, health checks, metrics)
- ✅ **Legal Compliance** (EEOC 80% rule, bias severity classification)
- ✅ **Actionable Insights** (Automated recommendations, fairness badges A+ to F)

---

## ⚠️ Deployment Requirements

### CRITICAL: System Dependencies Required

AIF360 requires **system-level packages** that are NOT available on most cloud **free tiers**:

```bash
gcc, g++, gfortran, libblas-dev, liblapack-dev, python3-dev
```

### Supported Platforms

| Platform | Free Tier | Paid Tier | Status |
|----------|-----------|-----------|--------|
| **Railway** | ✅ Yes ($5 credit) | ✅ Yes ($5/month) | 🏆 **RECOMMENDED** |
| **Fly.io** | ✅ Yes | ✅ Yes | ✅ Good alternative |
| **Render** | ❌ No | ✅ Yes ($7/month) | ✅ Works (paid only) |
| **Heroku** | ❌ Discontinued | ✅ Yes ($7/month) | ⚠️ Legacy |

**Recommendation:** Use **Railway** (free $5 credit, Docker support, faster builds).

---

## 🚀 Quick Start

### Deploy to Railway (FREE - Recommended)

```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Navigate to project
cd aif360-service

# Deploy
railway init
railway up

# Get URL
railway domain
```

**⏱️ Time:** 10 minutes  
**💰 Cost:** $0 (uses free $5 credit)  
**📖 Full Guide:** [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md)

### 1. Local Development

```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/fairness-api.git
cd fairness-api/aif360-service

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies (takes 5-10 minutes)
pip install -r requirements.txt

# Run server
cd app
python main.py
```

**API Docs:** http://localhost:8000/docs

### 2. Docker Deployment

```powershell
# Build image
docker build -t fairness-api .

# Run container
docker run -d -p 8000:8000 --name fairness-api fairness-api:latest

# Check logs
docker logs fairness-api -f
```

### 3. Test API

```powershell
# Health check
curl http://localhost:8000/health

# Analyze fairness
$payload = @'
{
  "applications": [
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
    {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "male", "decision": 0, "ground_truth": 0},
    {"protected_attribute": "female", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 0},
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 1, "ground_truth": 1}
  ],
  "protected_attribute_name": "gender"
}
'@

Invoke-RestMethod -Uri "http://localhost:8000/analyze" `
  -Method POST `
  -ContentType "application/json" `
  -Body $payload
```

---

## 📊 API Endpoints

### `POST /analyze`

Perform comprehensive fairness analysis.

**Request:**
```json
{
  "applications": [
    {"protected_attribute": "male", "decision": 1, "ground_truth": 1},
    {"protected_attribute": "female", "decision": 0, "ground_truth": 1}
  ],
  "protected_attribute_name": "gender",
  "favorable_label": 1
}
```

**Response:**
```json
{
  "bias_detected": true,
  "fairness_badge": {
    "grade": "C",
    "score": 65.3,
    "level": "Fair Concerns",
    "color": "#fd7e14"
  },
  "fairness_metrics": {
    "statistical_parity_difference": 0.156,
    "disparate_impact_ratio": 0.72,
    "equal_opportunity_difference": 0.089
  },
  "violations": [
    {
      "metric": "disparate_impact_ratio",
      "value": 0.72,
      "threshold": 0.8,
      "severity": "medium",
      "interpretation": "Violates EEOC 80% rule"
    }
  ],
  "recommendations": [
    "🚨 LEGAL RISK: Disparate impact detected",
    "Action: Conduct adverse impact analysis",
    "Consider: Implement blind resume screening"
  ]
}
```

### `GET /health`

Health check endpoint.

```json
{
  "status": "healthy",
  "aif360_available": true,
  "timestamp": "2025-12-05T10:30:00Z"
}
```

### `GET /metrics`

Prometheus-style metrics.

```json
{
  "total_requests": 1523,
  "analyses_completed": 1489,
  "success_rate": 0.9776
}
```

---

## 📈 Fairness Metrics Explained

### 1. Statistical Parity (Demographic Parity)
**Question:** Are all groups hired at equal rates?

**Formula:** `P(hired | male) - P(hired | female)`

**Threshold:** < 0.1 (10%)

### 2. Disparate Impact (80% Rule)
**Question:** Is the lowest-hired group hired at ≥80% the rate of highest-hired group?

**Formula:** `min(rate) / max(rate)`

**Legal Threshold:** ≥ 0.8 (EEOC)

### 3. Equal Opportunity
**Question:** Do qualified candidates from all groups have equal chances?

**Formula:** `TPR_male - TPR_female`

**Threshold:** < 0.1

### 4. Equalized Odds (Average Odds)
**Question:** Does the model make equal mistakes across groups?

**Formula:** `avg(|TPR_diff|, |FPR_diff|)`

**Threshold:** < 0.1

### 5. Predictive Parity
**Question:** Are positive predictions equally accurate?

**Formula:** `Precision_male - Precision_female`

**Threshold:** < 0.1

---

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
│   (main.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  AIF360FairnessEngine       │
│  ┌───────────────────────┐  │
│  │ BinaryLabelDataset    │  │
│  │ ClassificationMetric  │  │
│  │ Bias Detection        │  │
│  │ Recommendations       │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
         │
         ▼
┌─────────────────┐
│   JSON Response │
│   - Metrics     │
│   - Violations  │
│   - Recs        │
└─────────────────┘
```

---

## 📁 Project Structure

```
aif360-service/
├── app/
│   ├── __init__.py
│   └── main.py              # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_analysis.py     # Unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── render.yaml             # Render deployment config
├── DEPLOYMENT_GUIDE.md     # Complete deployment instructions
└── README.md               # This file
```

---

## 🧪 Testing

```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_analysis.py::test_analyze_clear_bias -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 🚢 Deployment

### Render (PAID TIER REQUIRED)

1. **Create `render.yaml`** (already included)
2. **Push to GitHub**
3. **Connect to Render Dashboard**
4. **Select Starter Plan** ($7/month minimum)
5. **Deploy**

**Full instructions:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Railway (Free Tier Available)

```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Fly.io (Free Tier Available)

```bash
fly auth login
fly launch
fly deploy
```

---

## 🔒 Security Considerations

- ✅ **Input Validation:** Pydantic models with strict type checking
- ✅ **CORS:** Configurable allowed origins (set in production)
- ✅ **Rate Limiting:** Implement in production (e.g., with slowapi)
- ✅ **Authentication:** Add JWT/OAuth for protected endpoints
- ✅ **HTTPS:** Enable TLS in production
- ✅ **Secrets:** Use environment variables (never commit tokens)

---

## 📚 Documentation

- **API Docs:** `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **Deployment Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **AIF360 Docs:** https://aif360.readthedocs.io/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM Research:** AIF360 library
- **FastAPI:** Modern Python web framework
- **Render/Railway/Fly.io:** Cloud deployment platforms

---

## 📞 Support

- **Issues:** https://github.com/YOUR_USERNAME/fairness-api/issues
- **Discussions:** https://github.com/YOUR_USERNAME/fairness-api/discussions
- **Email:** your.email@example.com

---

## 🎓 Academic Use

If you use this in academic research, please cite:

```bibtex
@software{aif360_fairness_api,
  title={AIF360 Enterprise Fairness API},
  author={Your Name},
  year={2025},
  url={https://github.com/YOUR_USERNAME/fairness-api}
}
```

Also cite the original AIF360 paper:

```bibtex
@inproceedings{bellamy2019ai,
  title={AI Fairness 360: An extensible toolkit for detecting and mitigating algorithmic bias},
  author={Bellamy, Rachel KE and others},
  booktitle={IBM Journal of Research and Development},
  year={2019}
}
```

---

<div align="center">

**Built with ❤️ for fair AI hiring**

[Documentation](DEPLOYMENT_GUIDE.md) • [API Docs](http://localhost:8000/docs) • [Report Issues](https://github.com/YOUR_USERNAME/fairness-api/issues)

</div>
