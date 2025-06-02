#!/usr/bin/env python3
"""
Comprehensive Test Suite for Flask Currency Converter
Tests API functionality, live rates, and application endpoints
"""

import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import time

# Add the current directory to Python path to import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, converter, CurrencyConverter

class TestCurrencyConverter(unittest.TestCase):
    """Test the CurrencyConverter class functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.converter = CurrencyConverter()
        self.converter.cache = {}  
    
    def test_fallback_rates_functionality(self):
        """Test Case 1: Fallback rates when API is unavailable"""
        print("Running Test Case 1: Fallback Rates Functionality")
        
        # Test fallback rates
        rates = self.converter._get_fallback_rates('USD')
        self.assertIsInstance(rates, dict)
        self.assertIn('EUR', rates)
        self.assertIn('GBP', rates)
        self.assertEqual(rates['USD'], 1.0)
        
        # Test conversion with different base currency
        rates_eur = self.converter._get_fallback_rates('EUR')
        self.assertIsInstance(rates_eur, dict)
        self.assertIn('USD', rates_eur)
        
        print("Test Case 1 PASSED: Fallback rates working correctly")
    
    def test_currency_conversion_logic(self):
        """Test Case 2: Currency conversion logic and validation"""
        print("Running Test Case 2: Currency Conversion Logic")
        
        # Test valid conversion
        result = self.converter.convert_currency(100, 'USD', 'EUR')
        self.assertTrue(result['success'])
        self.assertEqual(result['original_amount'], 100.0)
        self.assertEqual(result['from_currency'], 'USD')
        self.assertEqual(result['to_currency'], 'EUR')
        self.assertIsInstance(result['converted_amount'], float)
        
        # Test negative amount validation
        result = self.converter.convert_currency(-50, 'USD', 'EUR')
        self.assertFalse(result['success'])
        self.assertIn('negative', result['error'].lower())
        
        # Test invalid currency
        result = self.converter.convert_currency(100, 'USD', 'INVALID')
        self.assertFalse(result['success'])
        self.assertIn('not supported', result['error'])
        
        print(" Test Case 2 PASSED: Currency conversion logic working correctly")
    
    def test_caching_mechanism(self):
        """Test Case 4: Rate caching functionality"""
        print("Running Test Case 4: Caching Mechanism")
        # Clear cache before test
        self.converter.cache = {}
        
        # First call should cache the result
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'rates': {'EUR': 0.85}}
            mock_get.return_value = mock_response
            
            rates1 = self.converter.get_exchange_rates('USD')
            self.assertEqual(mock_get.call_count, 1)
            
            # Second call should use cache (no additional API call)
            rates2 = self.converter.get_exchange_rates('USD')
            self.assertEqual(mock_get.call_count, 1)  # Still only 1 call
            
            # Results should be identical
            self.assertEqual(rates1, rates2)
        
        print(" Test Case 4 PASSED: Caching mechanism working correctly")
    
    def test_health_status_check(self):
        """Test Case 5: Application health monitoring"""
        print(" Running Test Case 5: Health Status Check")
        
        health = self.converter.get_health_status()
        self.assertIsInstance(health, dict)
        self.assertIn('status', health)
        self.assertIn('timestamp', health)
        self.assertIn('environment', health)
        self.assertIn('supported_currencies', health)
        
        # Health should be either 'healthy' or 'unhealthy'
        self.assertIn(health['status'], ['healthy', 'unhealthy'])
        
        print(" Test Case 5 PASSED: Health status monitoring working")


class TestFlaskApplication(unittest.TestCase):
    """Test the Flask application endpoints"""
    
    def setUp(self):
        """Set up Flask test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_main_page_loads(self):
        """Test Case 6: Main page accessibility"""
        print(" Running Test Case 6: Main Page Loading")
        
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Currency Converter', response.data)
        self.assertIn(b'Live exchange rates', response.data)
        
        print(" Test Case 6 PASSED: Main page loads correctly")
    
    def test_conversion_endpoint(self):
        """Test Case 7: Currency conversion API endpoint"""
        print(" Running Test Case 7: Conversion API Endpoint")
        
        # Test valid conversion request
        response = self.app.post('/convert', data={
            'amount': '100',
            'from_currency': 'USD',
            'to_currency': 'EUR'
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        
        if data.get('success'):
            self.assertIn('converted_amount', data)
            self.assertIn('exchange_rate', data)
        
        # Test missing fields
        response = self.app.post('/convert', data={
            'amount': '100',
            # Missing currencies
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data.get('success', True))
        
        print(" Test Case 7 PASSED: Conversion endpoint working correctly")
    
    def test_api_endpoints(self):
        """Test Case 3: REST API endpoints functionality"""
        print(" Running Test Case 3: REST API Endpoints")
        
        # Test currencies endpoint
        response = self.app.get('/api/currencies')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('currencies', data)
        self.assertIsInstance(data['currencies'], list)

        if __name__ == '__main__':
            unittest.main(verbosity=2)
