"""
ShadowWall AI Core Application
Main application orchestrator that manages all components
"""

import asyncio
import logging
from typing import Dict, Any
from pathlib import Path

from .network.monitor import NetworkMonitor
from .ml.threat_detector import ThreatDetector
from .ml.behavioral_analyzer import BehavioralAnalyzer
from .honeypots.manager import HoneypotManager
from .deception.controller import DeceptionController
from .intelligence.threat_intel import ThreatIntelligence
from .dashboard.advanced_server import NextGenDashboardServer
from .sandbox.emulator import SandboxEmulator
from ..utils.logger import get_logger
from ..database.connection import DatabaseManager

logger = get_logger(__name__)

class ShadowWallApplication:
    """Main ShadowWall AI application class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.running = False
        self.components = {}
        
        # Initialize database
        self.db_manager = DatabaseManager(config['database']['url'])
        
        # Initialize core components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all ShadowWall components"""
        logger.info("Initializing ShadowWall AI components...")
        
        # Network monitoring
        self.network_monitor = NetworkMonitor(
            interfaces=self.config['network']['interfaces'],
            config=self.config['network']
        )
        
        # Machine Learning components
        self.threat_detector = ThreatDetector(
            model_path=self.config['ml']['models_path'],
            config=self.config['ml']['threat_detection']
        )
        
        self.behavioral_analyzer = BehavioralAnalyzer(
            config=self.config['ml']['behavioral_analysis']
        )
        
        # Honeypot management
        self.honeypot_manager = HoneypotManager(
            config=self.config['honeypots']
        )
        
        # Deception controller
        self.deception_controller = DeceptionController(
            honeypot_manager=self.honeypot_manager,
            config=self.config
        )
        
        # Threat intelligence
        self.threat_intel = ThreatIntelligence(
            config=self.config['threat_intel']
        )
        
        # Advanced Dashboard server
        dashboard_config = self.config.get('dashboard', {})
        self.dashboard_server = NextGenDashboardServer(
            host=dashboard_config.get('host', '0.0.0.0'),
            port=dashboard_config.get('port', 8081)
        )
        # Set database path after initialization
        self.dashboard_server.db_path = self.config.get('database', {}).get('url', 'data/shadowwall.db')
        
        # Sandbox emulator
        if self.config['sandbox']['enabled']:
            self.sandbox_emulator = SandboxEmulator(
                config=self.config['sandbox']
            )
        
        # Store components for lifecycle management
        self.components = {
            'network_monitor': self.network_monitor,
            'threat_detector': self.threat_detector,
            'behavioral_analyzer': self.behavioral_analyzer,
            'honeypot_manager': self.honeypot_manager,
            'deception_controller': self.deception_controller,
            'threat_intel': self.threat_intel,
            'dashboard_server': self.dashboard_server
        }
        
        if hasattr(self, 'sandbox_emulator'):
            self.components['sandbox_emulator'] = self.sandbox_emulator
    
    async def start(self):
        """Start all ShadowWall components"""
        logger.info("Starting ShadowWall AI...")
        
        try:
            # Initialize database
            await self.db_manager.initialize()
            
            # Start components in order
            await self._start_threat_intelligence()
            await self._start_ml_components()
            await self._start_network_monitoring()
            await self._start_honeypots()
            await self._start_deception_controller()
            await self._start_dashboard()
            
            if 'sandbox_emulator' in self.components:
                await self._start_sandbox()
            
            self.running = True
            logger.info("ShadowWall AI started successfully!")
            
        except Exception as e:
            logger.error(f"Failed to start ShadowWall AI: {e}")
            await self.shutdown()
            raise
    
    async def _start_threat_intelligence(self):
        """Start threat intelligence feeds"""
        logger.info("Starting threat intelligence...")
        await self.threat_intel.start()
        
        # Setup event handlers
        self.threat_intel.on_new_ioc(self._handle_new_ioc)
    
    async def _start_ml_components(self):
        """Start machine learning components"""
        logger.info("Starting ML components...")
        
        # Load and initialize models
        await self.threat_detector.initialize()
        await self.behavioral_analyzer.initialize()
        
        # Setup event handlers
        self.threat_detector.on_threat_detected(self._handle_threat_detected)
        self.behavioral_analyzer.on_anomaly_detected(self._handle_anomaly_detected)
    
    async def _start_network_monitoring(self):
        """Start network monitoring"""
        logger.info("Starting network monitoring...")
        await self.network_monitor.start()
        
        # Connect network events to ML pipeline
        self.network_monitor.on_packet_captured(self._process_network_packet)
        self.network_monitor.on_connection_event(self._process_connection_event)
    
    async def _start_honeypots(self):
        """Start honeypot management"""
        logger.info("Starting honeypot management...")
        await self.honeypot_manager.start()
        
        # Setup event handlers
        self.honeypot_manager.on_interaction(self._handle_honeypot_interaction)
    
    async def _start_deception_controller(self):
        """Start deception controller"""
        logger.info("Starting deception controller...")
        await self.deception_controller.start()
    
    async def _start_dashboard(self):
        """Start advanced dashboard server"""
        logger.info("Starting ShadowWall AI Next-Generation Dashboard...")
        
        # Setup dashboard integration with other components
        self._setup_dashboard_integration()
        
        await self.dashboard_server.start_server()
    
    def _setup_dashboard_integration(self):
        """Setup integration between dashboard and other components"""
        # Pass references to other components for real-time data access
        self.dashboard_server.network_monitor = self.network_monitor
        self.dashboard_server.threat_detector = self.threat_detector
        self.dashboard_server.behavioral_analyzer = self.behavioral_analyzer
        self.dashboard_server.honeypot_manager = self.honeypot_manager
        self.dashboard_server.threat_intel = self.threat_intel
        if hasattr(self, 'sandbox_emulator'):
            self.dashboard_server.sandbox_emulator = self.sandbox_emulator
    
    async def _start_sandbox(self):
        """Start sandbox emulator"""
        logger.info("Starting sandbox emulator...")
        await self.sandbox_emulator.start()
    
    async def run_forever(self):
        """Keep the application running"""
        while self.running:
            await asyncio.sleep(1)
            
            # Perform periodic health checks
            await self._health_check()
    
    async def _health_check(self):
        """Perform health checks on all components"""
        for name, component in self.components.items():
            if hasattr(component, 'health_check'):
                try:
                    await component.health_check()
                except Exception as e:
                    logger.error(f"Health check failed for {name}: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down ShadowWall AI...")
        self.running = False
        
        # Shutdown components in reverse order
        for name, component in reversed(list(self.components.items())):
            try:
                if hasattr(component, 'stop'):
                    await component.stop()
                logger.info(f"Stopped {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
    
    async def stop(self):
        """Alias for shutdown method"""
        await self.shutdown()
        
        # Close database connections
        await self.db_manager.close()
        
        logger.info("ShadowWall AI shutdown complete")
    
    # Event handlers
    async def _handle_new_ioc(self, ioc_data):
        """Handle new indicators of compromise"""
        logger.info(f"New IOC received: {ioc_data['type']}")
        
        # Update ML models with new threat data
        await self.threat_detector.update_threat_indicators(ioc_data)
        
        # Update honeypot configurations
        await self.deception_controller.adapt_to_new_threat(ioc_data)
    
    async def _handle_threat_detected(self, threat_data):
        """Handle detected threats"""
        logger.warning(f"Threat detected: {threat_data['type']} from {threat_data['source']}")
        
        # Trigger deception responses
        await self.deception_controller.respond_to_threat(threat_data)
        
        # Update dashboard via WebSocket
        await self.dashboard_server.broadcast_to_channel("threats", {
            "type": "threat_detected",
            "data": threat_data
        })
    
    async def _handle_anomaly_detected(self, anomaly_data):
        """Handle behavioral anomalies"""
        logger.info(f"Anomaly detected: {anomaly_data['type']}")
        
        # Feed anomaly to threat detector
        await self.threat_detector.analyze_anomaly(anomaly_data)
    
    async def _handle_honeypot_interaction(self, interaction_data):
        """Handle honeypot interactions"""
        logger.info(f"Honeypot interaction: {interaction_data['service']} from {interaction_data['source_ip']}")
        
        # Learn from attacker behavior
        await self.behavioral_analyzer.learn_from_interaction(interaction_data)
        
        # Update deception strategies
        await self.deception_controller.learn_from_interaction(interaction_data)
        
        # Update dashboard via WebSocket
        await self.dashboard_server.broadcast_to_channel("honeypots", {
            "type": "honeypot_interaction",
            "data": interaction_data
        })
    
    async def _process_network_packet(self, packet_data):
        """Process captured network packets"""
        # Feed to behavioral analyzer
        await self.behavioral_analyzer.process_packet(packet_data)
        
        # Check against threat indicators
        await self.threat_detector.analyze_packet(packet_data)
    
    async def _process_connection_event(self, connection_data):
        """Process network connection events"""
        # Analyze connection patterns
        await self.behavioral_analyzer.process_connection(connection_data)
        
        # Check for suspicious patterns
        await self.threat_detector.analyze_connection(connection_data)
