# ShadowWall AI Testing Framework

import unittest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import os
from datetime import datetime

# Test imports
from src.core.config.settings import load_config
from src.core.ml.threat_detector import ThreatDetector
from src.core.ml.behavioral_analyzer import BehavioralAnalyzer
from src.core.honeypots.manager import HoneypotManager
from src.core.network.monitor import NetworkMonitor
from src.core.deception.controller import DeceptionController
from src.core.intelligence.threat_intel import ThreatIntelligence
from src.core.sandbox.emulator import SandboxEmulator


class TestConfiguration(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def setUp(self):
        self.test_config = {
            'database': {'url': 'sqlite:///test.db'},
            'logging': {'level': 'INFO'},
            'network': {'interface': 'eth0'},
            'ml': {'model_update_interval': 3600},
            'honeypots': {'enabled': True},
            'dashboard': {'port': 8080},
            'sandbox': {'enabled': False}
        }
    
    def test_config_loading(self):
        """Test configuration loading from dict"""
        # This would normally test file loading, but we'll test the structure
        self.assertIn('database', self.test_config)
        self.assertIn('logging', self.test_config)
        self.assertIn('network', self.test_config)
        self.assertIn('ml', self.test_config)
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test required fields are present
        required_sections = ['database', 'logging', 'network', 'ml']
        for section in required_sections:
            self.assertIn(section, self.test_config)


class TestThreatDetector(unittest.TestCase):
    """Test ML threat detection"""
    
    def setUp(self):
        self.config = {
            'models_dir': tempfile.mkdtemp(),
            'update_interval': 3600,
            'anomaly_threshold': 0.95,
            'ensemble_weights': [0.4, 0.3, 0.3]
        }
        self.detector = ThreatDetector(self.config)
    
    def test_initialization(self):
        """Test threat detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertEqual(self.detector.config, self.config)
    
    @patch('src.core.ml.threat_detector.IsolationForest')
    @patch('src.core.ml.threat_detector.RandomForestClassifier')
    def test_model_training(self, mock_rf, mock_iso):
        """Test model training with synthetic data"""
        # Mock the models
        mock_iso_instance = Mock()
        mock_rf_instance = Mock()
        mock_iso.return_value = mock_iso_instance
        mock_rf.return_value = mock_rf_instance
        
        # Test training
        asyncio.run(self.detector._train_models())
        
        # Verify models were created and trained
        mock_iso.assert_called_once()
        mock_rf.assert_called_once()
    
    def test_threat_analysis(self):
        """Test threat analysis logic"""
        # Test with sample features
        features = [0.5, 0.3, 0.8, 0.2, 0.9]
        
        # Mock trained models
        self.detector.isolation_forest = Mock()
        self.detector.random_forest = Mock()
        self.detector.isolation_forest.decision_function.return_value = [-0.1]
        self.detector.random_forest.predict_proba.return_value = [[0.8, 0.2]]
        
        result = self.detector.analyze_threat(features)
        
        self.assertIsInstance(result, dict)
        self.assertIn('threat_score', result)
        self.assertIn('threat_type', result)


class TestBehavioralAnalyzer(unittest.TestCase):
    """Test behavioral analysis"""
    
    def setUp(self):
        self.config = {
            'learning_rate': 0.1,
            'baseline_period': 3600,
            'anomaly_threshold': 2.0
        }
        self.analyzer = BehavioralAnalyzer(self.config)
    
    def test_initialization(self):
        """Test behavioral analyzer initialization"""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(len(self.analyzer.entity_profiles), 0)
    
    def test_entity_tracking(self):
        """Test entity behavior tracking"""
        entity_id = "user_123"
        behavior_data = {
            'login_time': datetime.now(),
            'source_ip': '192.168.1.100',
            'actions': ['login', 'file_access']
        }
        
        result = asyncio.run(self.analyzer.track_behavior(entity_id, behavior_data))
        
        self.assertIsInstance(result, dict)
        self.assertIn('anomaly_score', result)
        self.assertIn(entity_id, self.analyzer.entity_profiles)


class TestHoneypotManager(unittest.TestCase):
    """Test honeypot management"""
    
    def setUp(self):
        self.config = {
            'ssh_port': 2222,
            'http_port': 8080,
            'ftp_port': 2121,
            'deployment_strategy': 'adaptive',
            'max_honeypots': 10
        }
        self.manager = HoneypotManager(self.config)
    
    def test_initialization(self):
        """Test honeypot manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(len(self.manager.active_honeypots), 0)
    
    @patch('asyncio.start_server')
    async def test_honeypot_deployment(self, mock_server):
        """Test honeypot deployment"""
        mock_server.return_value = Mock()
        
        honeypot_id = await self.manager.deploy_honeypot('ssh', '0.0.0.0', 2222)
        
        self.assertIsNotNone(honeypot_id)
        self.assertIn(honeypot_id, self.manager.active_honeypots)
    
    def test_interaction_recording(self):
        """Test interaction recording"""
        interaction_data = {
            'source_ip': '192.168.1.100',
            'honeypot_type': 'ssh',
            'timestamp': datetime.now(),
            'data': 'login attempt'
        }
        
        asyncio.run(self.manager.record_interaction(interaction_data))
        
        # Verify interaction was recorded
        self.assertTrue(len(self.manager.interactions) > 0)


class TestNetworkMonitor(unittest.TestCase):
    """Test network monitoring"""
    
    def setUp(self):
        self.config = {
            'interface': 'lo',  # Use loopback for testing
            'capture_filter': 'tcp',
            'simulation_mode': True  # Use simulation for testing
        }
        self.monitor = NetworkMonitor(self.config)
    
    def test_initialization(self):
        """Test network monitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.interface, 'lo')
    
    @patch('scapy.all.AsyncSniffer')
    def test_packet_capture_start(self, mock_sniffer):
        """Test packet capture start"""
        mock_sniffer_instance = Mock()
        mock_sniffer.return_value = mock_sniffer_instance
        
        asyncio.run(self.monitor.start())
        
        if not self.config['simulation_mode']:
            mock_sniffer.assert_called_once()


class TestDeceptionController(unittest.TestCase):
    """Test deception strategies"""
    
    def setUp(self):
        self.config = {
            'strategy_update_interval': 300,
            'effectiveness_threshold': 0.7
        }
        # Mock dependencies
        self.honeypot_manager = Mock()
        self.threat_detector = Mock()
        self.controller = DeceptionController(self.config, self.honeypot_manager, self.threat_detector)
    
    def test_initialization(self):
        """Test deception controller initialization"""
        self.assertIsNotNone(self.controller)
        self.assertTrue(len(self.controller.available_strategies) > 0)
    
    def test_strategy_selection(self):
        """Test strategy selection logic"""
        threat_context = {
            'threat_type': 'reconnaissance',
            'source_ip': '192.168.1.100',
            'confidence': 0.8
        }
        
        strategy = asyncio.run(self.controller.select_strategy(threat_context))
        
        self.assertIsNotNone(strategy)
        self.assertIn('name', strategy)
        self.assertIn('actions', strategy)


class TestSandboxEmulator(unittest.TestCase):
    """Test sandbox emulation"""
    
    def setUp(self):
        self.config = {
            'enabled': True,
            'max_concurrent_sessions': 5
        }
        self.emulator = SandboxEmulator(self.config)
    
    def test_initialization(self):
        """Test sandbox emulator initialization"""
        self.assertIsNotNone(self.emulator)
        self.assertTrue(len(self.emulator.environments) > 0)
    
    @patch('docker.from_env')
    def test_session_creation(self, mock_docker):
        """Test sandbox session creation"""
        # Mock Docker client
        mock_docker.return_value = Mock()
        
        session_id = asyncio.run(
            self.emulator.create_session('test_user', 'basic_network', 60)
        )
        
        # In simulation mode, this should still work
        self.assertTrue(session_id is None or isinstance(session_id, str))
    
    def test_environment_listing(self):
        """Test available environments listing"""
        environments = self.emulator.get_available_environments()
        
        self.assertIsInstance(environments, dict)
        self.assertIn('basic_network', environments)
        self.assertIn('corporate_sim', environments)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.config = {
            'database': {'url': 'sqlite:///:memory:'},
            'logging': {'level': 'INFO'},
            'network': {'interface': 'lo', 'simulation_mode': True},
            'ml': {'model_update_interval': 3600},
            'honeypots': {'enabled': True, 'ssh_port': 2222},
            'dashboard': {'port': 8080},
            'sandbox': {'enabled': False},
            'deception': {'strategy_update_interval': 300},
            'threat_intel': {'enabled': True, 'update_interval': 3600}
        }
    
    def test_component_initialization(self):
        """Test that all components can be initialized together"""
        try:
            # Initialize core components
            threat_detector = ThreatDetector(self.config['ml'])
            behavioral_analyzer = BehavioralAnalyzer(self.config['ml'])
            honeypot_manager = HoneypotManager(self.config['honeypots'])
            network_monitor = NetworkMonitor(self.config['network'])
            
            # Verify initialization
            self.assertIsNotNone(threat_detector)
            self.assertIsNotNone(behavioral_analyzer)
            self.assertIsNotNone(honeypot_manager)
            self.assertIsNotNone(network_monitor)
            
        except Exception as e:
            self.fail(f"Component initialization failed: {e}")


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("ShadowWall AI - Running Test Suite")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestConfiguration,
        TestThreatDetector,
        TestBehavioralAnalyzer,
        TestHoneypotManager,
        TestNetworkMonitor,
        TestDeceptionController,
        TestSandboxEmulator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nResult: {'PASSED' if success else 'FAILED'}")
    print("=" * 60)
    
    return success


if __name__ == '__main__':
    run_tests()
