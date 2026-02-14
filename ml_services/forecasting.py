"""
Machine Learning Forecasting Module
Implements ARIMA, LSTM, Random Forest, and ensemble methods for demand prediction
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

# Statistical Models
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    STATSMODELS_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Statsmodels not available: {e}")
    STATSMODELS_AVAILABLE = False
    ARIMA = None
    SARIMAX = None

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    SKLEARN_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Scikit-learn not available: {e}")
    SKLEARN_AVAILABLE = False

# Deep Learning
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    TENSORFLOW_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"TensorFlow not available: {e}")
    TENSORFLOW_AVAILABLE = False

# Time Series
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except (ImportError, OSError) as e:
    print(f"Prophet not available: {e}")
    PROPHET_AVAILABLE = False


class DemandForecaster:
    """
    Unified demand forecasting engine supporting multiple algorithms
    """
    
    def __init__(self, method='arima'):
        """
        Initialize forecaster with specified method
        
        Args:
            method: 'arima', 'lstm', 'random_forest', 'prophet', 'ensemble'
        """
        self.method = method
        self.model = None
        self.scaler = MinMaxScaler()
        self.history = []
        
    def prepare_data(self, sales_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare time series data for training
        
        Args:
            sales_data: DataFrame with 'date' and 'quantity' columns
            
        Returns:
            X, y arrays for training
        """
        # Sort by date
        sales_data = sales_data.sort_values('date')
        
        # Extract features
        sales_data['day_of_week'] = pd.to_datetime(sales_data['date']).dt.dayofweek
        sales_data['day_of_month'] = pd.to_datetime(sales_data['date']).dt.day
        sales_data['month'] = pd.to_datetime(sales_data['date']).dt.month
        sales_data['quarter'] = pd.to_datetime(sales_data['date']).dt.quarter
        
        # Rolling statistics
        sales_data['rolling_mean_7'] = sales_data['quantity'].rolling(window=7, min_periods=1).mean()
        sales_data['rolling_std_7'] = sales_data['quantity'].rolling(window=7, min_periods=1).std()
        sales_data['rolling_mean_30'] = sales_data['quantity'].rolling(window=30, min_periods=1).mean()
        
        # Lag features
        for lag in [1, 7, 14, 30]:
            sales_data[f'lag_{lag}'] = sales_data['quantity'].shift(lag)
        
        # Fill NaN values
        sales_data = sales_data.fillna(method='bfill').fillna(0)
        
        return sales_data
        
    def train_arima(self, data: pd.Series, order=(5,1,0)):
        """Train ARIMA model for time series forecasting"""
        try:
            self.model = ARIMA(data, order=order)
            self.model = self.model.fit()
            return True
        except Exception as e:
            print(f"ARIMA training failed: {e}")
            # Fallback to simpler model
            self.model = ARIMA(data, order=(1,1,1))
            self.model = self.model.fit()
            return True
            
    def train_lstm(self, data: np.ndarray, lookback=30, epochs=50):
        """Train LSTM neural network for time series forecasting"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow not available for LSTM")
            
        # Prepare sequences
        X, y = [], []
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))
        
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
            
        X, y = np.array(X), np.array(y)
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Build LSTM model
        self.model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        self.model.fit(X, y, batch_size=32, epochs=epochs, verbose=0, validation_split=0.1)
        
        return True
        
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series):
        """Train Random Forest for demand prediction"""
        feature_cols = [col for col in X.columns if col not in ['date', 'quantity']]
        X_train = X[feature_cols]
        
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.model.fit(X_train, y)
        
        return True
        
    def train_prophet(self, data: pd.DataFrame):
        """Train Facebook Prophet model"""
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not available")
            
        # Prophet requires 'ds' and 'y' columns
        prophet_data = data.rename(columns={'date': 'ds', 'quantity': 'y'})
        
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        self.model.fit(prophet_data)
        
        return True
        
    def predict(self, steps=30, X_future=None):
        """
        Generate forecast for future periods
        
        Args:
            steps: Number of periods to forecast
            X_future: Future features for supervised learning
            
        Returns:
            Array of predictions
        """
        if self.method == 'arima':
            forecast = self.model.forecast(steps=steps)
            return np.array(forecast)
            
        elif self.method == 'lstm':
            predictions = []
            last_sequence = self.scaler.transform(self.history[-30:].reshape(-1, 1))
            
            for _ in range(steps):
                pred = self.model.predict(last_sequence.reshape(1, 30, 1))
                predictions.append(pred[0, 0])
                last_sequence = np.append(last_sequence[1:], pred).reshape(-1, 1)
                
            return self.scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
            
        elif self.method == 'random_forest':
            if X_future is None:
                raise ValueError("Random Forest requires future features")
            return self.model.predict(X_future)
            
        elif self.method == 'prophet':
            future = self.model.make_future_dataframe(periods=steps)
            forecast = self.model.predict(future)
            return forecast['yhat'].tail(steps).values
            
        return np.zeros(steps)
        
    def calculate_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Calculate forecast accuracy metrics"""
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
        r2 = r2_score(y_true, y_pred)
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2': float(r2)
        }


class StockoutPredictor:
    """Predict probability of stockout events"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        
    def prepare_features(self, inventory_data: pd.DataFrame) -> pd.DataFrame:
        """Extract features for stockout prediction"""
        features = pd.DataFrame()
        
        features['current_stock'] = inventory_data['quantity_on_hand']
        features['avg_daily_sales'] = inventory_data['avg_sales']
        features['days_of_stock'] = features['current_stock'] / (features['avg_daily_sales'] + 0.1)
        features['reorder_point'] = inventory_data['reorder_point']
        features['lead_time'] = inventory_data['lead_time_days']
        features['stock_variance'] = inventory_data['stock_variance']
        features['is_peak_season'] = inventory_data['is_peak_season']
        
        return features
        
    def train(self, X: pd.DataFrame, y: np.ndarray):
        """Train stockout prediction model"""
        self.model.fit(X, y)
        
    def predict_stockout_risk(self, X: pd.DataFrame) -> np.ndarray:
        """Predict stockout risk (0-1 probability)"""
        predictions = self.model.predict(X)
        return np.clip(predictions, 0, 1)


class ProductRecommender:
    """Product recommendation using collaborative filtering and clustering"""
    
    def __init__(self):
        from sklearn.cluster import KMeans
        from sklearn.metrics.pairwise import cosine_similarity
        
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.product_features = None
        self.similarity_matrix = None
        
    def build_features(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """Build product feature matrix from sales data"""
        # Pivot to get product-customer matrix
        product_matrix = sales_data.pivot_table(
            index='product_id',
            columns='customer_id',
            values='quantity',
            fill_value=0
        )
        
        self.product_features = product_matrix
        return product_matrix
        
    def fit(self, features: pd.DataFrame):
        """Cluster products and calculate similarity"""
        # K-Means clustering
        self.kmeans.fit(features)
        
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        self.similarity_matrix = cosine_similarity(features)
        
    def recommend_products(self, product_id: int, n_recommendations=5) -> List[int]:
        """Recommend similar products"""
        if self.similarity_matrix is None:
            return []
            
        product_idx = list(self.product_features.index).index(product_id)
        similarities = self.similarity_matrix[product_idx]
        
        # Get top N similar products
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        recommended_ids = [self.product_features.index[i] for i in similar_indices]
        
        return recommended_ids
        
    def get_cluster(self, product_id: int) -> int:
        """Get cluster assignment for product"""
        product_idx = list(self.product_features.index).index(product_id)
        features = self.product_features.iloc[product_idx].values.reshape(1, -1)
        return int(self.kmeans.predict(features)[0])


class SalesTrendAnalyzer:
    """Analyze sales trends and patterns"""
    
    @staticmethod
    def detect_trend(data: pd.Series) -> str:
        """Detect if sales are trending up, down, or stable"""
        from scipy import stats
        
        x = np.arange(len(data))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, data.values)
        
        if p_value > 0.05:
            return 'stable'
        elif slope > 0:
            return 'increasing'
        else:
            return 'decreasing'
            
    @staticmethod
    def detect_seasonality(data: pd.Series) -> Dict:
        """Detect seasonal patterns in sales data"""
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        if len(data) < 14:
            return {'has_seasonality': False}
            
        try:
            result = seasonal_decompose(data, model='additive', period=7)
            
            # Calculate strength of seasonality
            seasonal_strength = np.var(result.seasonal) / np.var(result.resid + result.seasonal)
            
            return {
                'has_seasonality': seasonal_strength > 0.3,
                'seasonal_strength': float(seasonal_strength),
                'trend': result.trend.dropna().tolist()[-7:],
                'seasonal': result.seasonal.tolist()[-7:]
            }
        except:
            return {'has_seasonality': False}
            
    @staticmethod
    def calculate_growth_rate(data: pd.Series, period='monthly') -> float:
        """Calculate growth rate over specified period"""
        if len(data) < 2:
            return 0.0
            
        start_value = data.iloc[:len(data)//2].mean()
        end_value = data.iloc[len(data)//2:].mean()
        
        if start_value == 0:
            return 0.0
            
        growth_rate = ((end_value - start_value) / start_value) * 100
        return float(growth_rate)
