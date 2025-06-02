#!/usr/bin/env python3
"""
Flask Currency Converter Application
A web-based currency converter with live exchange rates
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import os
from datetime import datetime, timedelta
import json
from functools import wraps
import time

app = Flask(__name__)

class CurrencyConverter:
    def __init__(self):
        self.api_key = os.getenv('EXCHANGE_API_KEY', 'demo')  # Use demo for testing
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.backup_url = "https://api.fixer.io/latest"  # Backup API
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        self.app_env = os.getenv('APP_ENV', 'development')
        self.api_endpoint = os.getenv('API_ENDPOINT', 'localhost:5000')
        
        # Fallback rates for offline mode or API failures
        self.fallback_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'CAD': 1.25,
            'JPY': 110.0,
            'AUD': 1.35,
            'CHF': 0.92,
            'CNY': 6.45,
            'INR': 74.5,
            'KRW': 1180.0
        }
    
    def get_exchange_rates(self, base_currency='USD', use_fallback=False):
        """Fetch live exchange rates from API with caching"""
        cache_key = f"rates_{base_currency}"
        current_time = time.time()
        
        # Check cache first
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_duration:
                return cached_data
        
        if use_fallback:
            return self._get_fallback_rates(base_currency)
        
        try:
            # Try primary API
            response = requests.get(
                f"{self.base_url}/{base_currency}",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                rates[base_currency] = 1.0  # Add base currency
                
                # Cache the result
                self.cache[cache_key] = (rates, current_time)
                return rates
            else:
                raise requests.RequestException(f"API returned {response.status_code}")
                
        except requests.RequestException as e:
            print(f"Primary API failed: {e}")
            # Fall back to backup rates
            return self._get_fallback_rates(base_currency)
    
    def _get_fallback_rates(self, base_currency='USD'):
        """Get fallback exchange rates when API is unavailable"""
        if base_currency == 'USD':
            return self.fallback_rates.copy()
        
        # Convert fallback rates to requested base currency
        usd_rate = self.fallback_rates.get(base_currency, 1.0)
        converted_rates = {}
        
        for currency, rate in self.fallback_rates.items():
            converted_rates[currency] = rate / usd_rate
        
        return converted_rates
    
    def convert_currency(self, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            
            # Get exchange rates
            rates = self.get_exchange_rates(from_currency)
            
            if to_currency not in rates:
                raise ValueError(f"Currency {to_currency} not supported")
            
            # Convert
            converted_amount = amount * rates[to_currency]
            
            return {
                'success': True,
                'original_amount': amount,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'converted_amount': round(converted_amount, 2),
                'exchange_rate': rates[to_currency],
                'timestamp': datetime.now().isoformat(),
                'data_source': 'live_api' if from_currency + '_USD' not in str(rates) else 'fallback'
            }
            
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': f"Conversion failed: {str(e)}"}
    
    def get_supported_currencies(self):
        """Get list of supported currencies"""
        try:
            rates = self.get_exchange_rates()
            return sorted(list(rates.keys()))
        except:
            return sorted(list(self.fallback_rates.keys()))
    
    def get_health_status(self):
        """Check application health status"""
        try:
            # Test basic functionality
            test_conversion = self.convert_currency(1, 'USD', 'EUR')
            api_status = 'online' if 'live_api' in str(test_conversion) else 'fallback'
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'environment': self.app_env,
                'api_endpoint': self.api_endpoint,
                'api_status': api_status,
                'supported_currencies': len(self.get_supported_currencies()),
                'cache_entries': len(self.cache)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Initialize converter
converter = CurrencyConverter()

# Routes
@app.route('/')
def index():
    """Main page with currency converter form"""
    currencies = converter.get_supported_currencies()
    return render_template('index.html', currencies=currencies)

@app.route('/convert', methods=['POST'])
def convert():
    """Handle currency conversion requests"""
    try:
        amount = request.form.get('amount')
        from_currency = request.form.get('from_currency')
        to_currency = request.form.get('to_currency')
        
        if not all([amount, from_currency, to_currency]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        result = converter.convert_currency(amount, from_currency, to_currency)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/convert')
def api_convert():
    """API endpoint for currency conversion"""
    try:
        amount = request.args.get('amount')
        from_currency = request.args.get('from', 'USD')
        to_currency = request.args.get('to', 'EUR')
        
        if not amount:
            return jsonify({'success': False, 'error': 'Amount parameter required'})
        
        result = converter.convert_currency(amount, from_currency, to_currency)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/currencies')
def api_currencies():
    """API endpoint to get supported currencies"""
    try:
        currencies = converter.get_supported_currencies()
        return jsonify({
            'success': True,
            'currencies': currencies,
            'count': len(currencies)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rates/<base_currency>')
def api_rates(base_currency):
    """API endpoint to get exchange rates for a base currency"""
    try:
        rates = converter.get_exchange_rates(base_currency.upper())
        return jsonify({
            'success': True,
            'base_currency': base_currency.upper(),
            'rates': rates,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_status = converter.get_health_status()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/info')
def app_info():
    """Application information endpoint"""
    return jsonify({
        'app_name': 'Currency Converter',
        'version': '1.0.0',
        'environment': converter.app_env,
        'api_endpoint': converter.api_endpoint,
        'python_version': '3.9+',
        'framework': 'Flask',
        'features': [
            'Live exchange rates',
            'Multiple currency support',
            'API endpoints',
            'Health monitoring',
            'Caching system',
            'Fallback rates'
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting Currency Converter Flask App")
    print(f"Environment: {converter.app_env}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    print(f"API Endpoint: {converter.api_endpoint}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)