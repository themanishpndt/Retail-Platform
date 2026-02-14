<<<<<<< HEAD
# Retail-Platform
=======
# AI-Driven Retail Analytics & Automation Platform

A comprehensive Django-based full-stack platform for retail inventory management, demand forecasting, and business intelligence using AI/ML and Computer Vision.

## 🎯 Overview

This platform addresses critical retail challenges:
- **Stockouts & Overstocking** - Prevent revenue loss through intelligent inventory management
- **Manual Tracking** - Automate inventory operations with real-time tracking
- **Poor Forecasting** - Predict demand accurately using ML models
- **Lack of Insights** - Generate actionable business intelligence through advanced analytics

## 🏗️ System Architecture

```
Data Sources (POS, ERP, Excel, Images)
        ↓
Data Ingestion & ETL Layer
        ↓
Django REST Backend (APIs)
        ↓
PostgreSQL Database
        ↓
ML Services (Forecasting) | CV Services (Vision)
        ↓
REST APIs (Django REST Framework)
        ↓
Web Dashboard | Mobile Apps
        ↓
Real-time Alerts & Notifications
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation (Local Development)

1. **Clone the repository**
```bash
git clone <repository-url>
cd retail_platform
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Set up database**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

7. **Start Celery (in another terminal)**
```bash
celery -A retail_core worker -l info
celery -A retail_core beat -l info
```

Access the application at `http://localhost:8000`

### Docker Installation (Recommended for Production)

```bash
docker-compose up -d
```

This will start:
- Django application (port 8000)
- PostgreSQL database
- Redis cache
- Celery worker
- Celery Beat scheduler

## 📚 Project Structure

```
retail_platform/
├── retail_core/           # Main Django project settings
├── products/              # Product management app
├── inventory/             # Inventory management app
├── orders/                # Orders & PO management
├── analytics/             # Sales analytics & insights
├── alerts/                # Alert system
├── ml_services/           # Machine learning (demand forecasting)
├── cv_services/           # Computer vision services
├── data_ingestion/        # ETL and data import
├── utils/                 # Utility functions
├── static/                # Static files
├── media/                 # User-uploaded files
├── templates/             # HTML templates
├── tests/                 # Test cases
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Multi-container setup
```

## 🔑 Key Features

### 1. Inventory Management
- Real-time stock tracking per store/location
- Automated reorder point calculations
- Stock movement tracking between locations
- Low stock and overstock alerts
- Physical inventory count management

### 2. Product Management
- SKU and barcode tracking
- Multi-supplier support
- Product categorization
- Cost and selling price management
- Automatic margin calculation

### 3. Order Management
- Sales order processing
- Purchase order generation
- Order line item tracking
- Status workflow management
- Order history and audit trail

### 4. Demand Forecasting (ML)
- Multiple forecasting models (ARIMA, LSTM, Prophet, Ensemble)
- Configurable training and validation
- Accuracy metrics (MAPE, RMSE, R²)
- Store and product-level predictions
- Confidence intervals for forecasts

### 5. Computer Vision
- Product detection using YOLO
- Shelf analysis and compliance checking
- Real-time stock level detection from images
- Stock visibility tracking
- Shelf quality scoring

### 6. Analytics & Insights
- Daily sales metrics aggregation
- Product-level sales analytics
- Category performance analysis
- Inventory health reports
- AI-generated business insights and recommendations

### 7. Alert System
- Configurable alert rules
- Multiple notification channels (Email, SMS, Slack, Webhook)
- Alert severity levels
- Alert acknowledgment and resolution tracking
- Alert history and audit trail

### 8. Data Ingestion
- Multi-source data import (CSV, JSON, Excel, APIs, POS, ERP)
- Field mapping and transformation
- Data validation rules
- Batch processing
- Audit trail for imported data

## 📊 API Endpoints

### Products
- `GET /api/v1/products/` - List products
- `POST /api/v1/products/` - Create product
- `GET /api/v1/products/{id}/` - Get product details
- `PUT /api/v1/products/{id}/` - Update product
- `DELETE /api/v1/products/{id}/` - Delete product

### Inventory
- `GET /api/v1/inventory/levels/` - List inventory levels
- `POST /api/v1/inventory/transactions/` - Create inventory transaction
- `GET /api/v1/inventory/transfers/` - List stock movements
- `POST /api/v1/inventory/transfers/` - Create stock transfer

### Orders
- `GET /api/v1/orders/` - List orders
- `POST /api/v1/orders/` - Create order
- `GET /api/v1/orders/{id}/` - Get order details
- `POST /api/v1/orders/{id}/ship/` - Ship order

### Analytics
- `GET /api/v1/analytics/daily-metrics/` - Daily sales metrics
- `GET /api/v1/analytics/product-analytics/` - Product performance
- `GET /api/v1/analytics/forecasts/` - Demand forecasts
- `GET /api/v1/analytics/insights/` - Business insights

### Alerts
- `GET /api/v1/alerts/` - List alerts
- `POST /api/v1/alerts/{id}/acknowledge/` - Acknowledge alert
- `POST /api/v1/alerts/{id}/resolve/` - Resolve alert

### Forecasting (ML)
- `POST /api/v1/forecasting/train/` - Train forecasting model
- `GET /api/v1/forecasting/models/` - List available models
- `POST /api/v1/forecasting/predict/` - Get predictions

### Computer Vision
- `POST /api/v1/vision/detect-stock/` - Detect stock levels from image
- `POST /api/v1/vision/analyze-shelf/` - Analyze shelf compliance
- `GET /api/v1/vision/results/` - Get analysis results

### Data Ingestion
- `POST /api/v1/data-ingestion/sources/` - Register data source
- `POST /api/v1/data-ingestion/import/` - Trigger data import
- `GET /api/v1/data-ingestion/jobs/` - View import jobs
- `GET /api/v1/data-ingestion/jobs/{id}/` - Get job details

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

```bash
# Get access token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/products/
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific app tests
pytest products/

# Run with coverage
pytest --cov=.

# Run specific test class
pytest tests/test_models.py::TestProductModel
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```
DEBUG=True                              # Debug mode
SECRET_KEY=your-secret-key             # Django secret key
DB_NAME=retail_db                       # Database name
DB_USER=retail_user                     # Database user
DB_PASSWORD=password                    # Database password
DB_HOST=localhost                       # Database host
REDIS_URL=redis://localhost:6379/0     # Redis connection
CORS_ALLOWED_ORIGINS=http://localhost:3000  # CORS settings
CELERY_BROKER_URL=redis://localhost:6379/0  # Celery broker
```

### ML Model Configuration

Configure forecasting models in admin panel:
- Model type (ARIMA, LSTM, Prophet, Ensemble)
- Training parameters
- Feature selection
- Validation strategy

### CV Model Configuration

Configure detection models:
- Model file paths
- Confidence thresholds
- Supported product categories
- Inference parameters

## 📈 Performance Tips

1. **Database Indexing** - Indexes are configured on frequently queried fields
2. **Caching** - Redis caches computed analytics
3. **Batch Processing** - Use Celery tasks for bulk operations
4. **Pagination** - APIs return paginated results (50 items/page)
5. **Database Queries** - Use `select_related()` and `prefetch_related()`

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
psql -U retail_user -d retail_db -h localhost

# Reset database
python manage.py migrate 0001
python manage.py migrate
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping
```

### Celery Not Processing Tasks
```bash
# Restart Celery worker
celery -A retail_core worker --purge -l info
```

## 🚀 Deployment

### Heroku Deployment
```bash
heroku create retail-analytics-app
heroku addons:create heroku-postgresql:standard-0
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
heroku run python manage.py migrate
```

### AWS Deployment
- Use EC2 for application server
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for media storage
- CloudFront for CDN

### Docker Deployment
```bash
docker-compose up -d
# Or with custom env file
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

## 📖 Documentation

- [API Documentation](http://localhost:8000/api/docs/) - Interactive API docs
- [Django Admin](http://localhost:8000/admin/) - Management interface
- [Data Model Diagram](docs/models.md) - Database schema
- [ML Pipeline](docs/ml_pipeline.md) - Forecasting workflow

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add your feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Email: support@retailanalytics.com
- Documentation: [Full documentation](https://retailanalytics.com/docs)

## 🗓️ Roadmap

- [ ] Real-time dashboard with WebSockets
- [ ] Mobile app (React Native/Flutter)
- [ ] Advanced predictive maintenance
- [ ] Supplier performance analytics
- [ ] Customer segmentation
- [ ] Dynamic pricing recommendations
- [ ] Integration with major POS systems
- [ ] Multi-language support
- [ ] Advanced report generation
- [ ] AI-powered chatbot support

## 🎉 Acknowledgments

Built with:
- Django & Django REST Framework
- PostgreSQL
- Redis & Celery
- TensorFlow, PyTorch, Scikit-learn
- OpenCV, YOLOv8
- React (frontend - to be added)
- React Native (mobile - to be added)

---

**Last Updated**: February 7, 2026

For the latest updates and information, visit the [project repository](https://github.com/your-repo).
>>>>>>> 5c2967d (Initial project commit)
