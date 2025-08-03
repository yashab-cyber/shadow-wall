"""
Deception Controller
Manages adaptive deception strategies and responds to threats
"""

import asyncio
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class DeceptionStrategy:
    """Deception strategy definition"""
    strategy_id: str
    name: str
    description: str
    target_threats: List[str]
    effectiveness_score: float
    deployment_cost: float
    implementation: Dict[str, Any]

@dataclass
class DeceptionResponse:
    """Response to a detected threat"""
    threat_id: str
    response_type: str
    strategies_deployed: List[str]
    success_probability: float
    deployment_time: datetime

class DeceptionController:
    """Controls adaptive deception strategies"""
    
    def __init__(self, honeypot_manager, config: Dict[str, Any]):
        self.honeypot_manager = honeypot_manager
        self.config = config
        self.strategies = self._initialize_strategies()
        self.active_responses = {}
        self.learning_data = {}
        
        # Strategy effectiveness tracking
        self.strategy_performance = {}
        
    def _initialize_strategies(self) -> Dict[str, DeceptionStrategy]:
        """Initialize available deception strategies"""
        strategies = {}
        
        # Honeypot deployment strategies
        strategies['adaptive_honeypot'] = DeceptionStrategy(
            strategy_id='adaptive_honeypot',
            name='Adaptive Honeypot Deployment',
            description='Deploy honeypots that mimic attacker targets',
            target_threats=['port_scan', 'service_enumeration', 'lateral_movement'],
            effectiveness_score=0.8,
            deployment_cost=0.3,
            implementation={
                'type': 'honeypot',
                'adaptive': True,
                'mimic_target': True
            }
        )
        
        strategies['decoy_services'] = DeceptionStrategy(
            strategy_id='decoy_services',
            name='Decoy Service Emulation',
            description='Create fake services that appear vulnerable',
            target_threats=['vulnerability_scan', 'exploit_attempt'],
            effectiveness_score=0.7,
            deployment_cost=0.2,
            implementation={
                'type': 'service_emulation',
                'fake_vulnerabilities': True,
                'interaction_logging': True
            }
        )
        
        strategies['network_deception'] = DeceptionStrategy(
            strategy_id='network_deception',
            name='Network Topology Deception',
            description='Create fake network segments and hosts',
            target_threats=['network_mapping', 'reconnaissance'],
            effectiveness_score=0.6,
            deployment_cost=0.4,
            implementation={
                'type': 'network_topology',
                'fake_hosts': True,
                'route_manipulation': True
            }
        )
        
        strategies['data_breadcrumbs'] = DeceptionStrategy(
            strategy_id='data_breadcrumbs',
            name='Deceptive Data Breadcrumbs',
            description='Plant fake credentials and data to mislead attackers',
            target_threats=['credential_theft', 'data_exfiltration'],
            effectiveness_score=0.9,
            deployment_cost=0.1,
            implementation={
                'type': 'data_deception',
                'fake_credentials': True,
                'canary_tokens': True
            }
        )
        
        strategies['behavioral_mimicry'] = DeceptionStrategy(
            strategy_id='behavioral_mimicry',
            name='Behavioral Mimicry',
            description='Mimic normal user behavior in honeypots',
            target_threats=['behavioral_analysis', 'ai_detection'],
            effectiveness_score=0.85,
            deployment_cost=0.5,
            implementation={
                'type': 'behavioral',
                'user_simulation': True,
                'traffic_generation': True
            }
        )
        
        return strategies
    
    async def start(self):
        """Start the deception controller"""
        logger.info("Starting deception controller...")
        
        # Start background tasks
        asyncio.create_task(self._monitor_strategy_effectiveness())
        asyncio.create_task(self._adaptive_strategy_updates())
        
        logger.info("Deception controller started")
    
    async def respond_to_threat(self, threat_data: Dict[str, Any]):
        """Respond to a detected threat with appropriate deception"""
        try:
            threat_type = threat_data.get('type', 'unknown')
            threat_id = threat_data.get('id', f"threat_{int(datetime.utcnow().timestamp())}")
            source_ip = threat_data.get('source_ip', 'unknown')
            
            logger.info(f"Responding to threat: {threat_type} from {source_ip}")
            
            # Select appropriate strategies
            suitable_strategies = self._select_strategies(threat_type, threat_data)
            
            if not suitable_strategies:
                logger.warning(f"No suitable deception strategies for threat type: {threat_type}")
                return
            
            # Deploy selected strategies
            deployed_strategies = []
            for strategy in suitable_strategies:
                success = await self._deploy_strategy(strategy, threat_data)
                if success:
                    deployed_strategies.append(strategy.strategy_id)
            
            # Record the response
            response = DeceptionResponse(
                threat_id=threat_id,
                response_type='adaptive_deception',
                strategies_deployed=deployed_strategies,
                success_probability=self._calculate_success_probability(deployed_strategies),
                deployment_time=datetime.utcnow()
            )
            
            self.active_responses[threat_id] = response
            
            logger.info(f"Deployed {len(deployed_strategies)} deception strategies for threat {threat_id}")
            
        except Exception as e:
            logger.error(f"Error responding to threat: {e}")
    
    def _select_strategies(self, threat_type: str, threat_data: Dict[str, Any]) -> List[DeceptionStrategy]:
        """Select appropriate deception strategies for a threat"""
        suitable_strategies = []
        
        for strategy in self.strategies.values():
            # Check if strategy targets this threat type
            if threat_type in strategy.target_threats or 'all' in strategy.target_threats:
                # Consider strategy effectiveness and cost
                if strategy.effectiveness_score > 0.5:  # Only use reasonably effective strategies
                    suitable_strategies.append(strategy)
        
        # Sort by effectiveness score
        suitable_strategies.sort(key=lambda x: x.effectiveness_score, reverse=True)
        
        # Return top 3 strategies to avoid over-deployment
        return suitable_strategies[:3]
    
    async def _deploy_strategy(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy a specific deception strategy"""
        try:
            implementation = strategy.implementation
            
            if implementation['type'] == 'honeypot':
                return await self._deploy_honeypot_strategy(strategy, threat_data)
            elif implementation['type'] == 'service_emulation':
                return await self._deploy_service_emulation(strategy, threat_data)
            elif implementation['type'] == 'network_topology':
                return await self._deploy_network_deception(strategy, threat_data)
            elif implementation['type'] == 'data_deception':
                return await self._deploy_data_breadcrumbs(strategy, threat_data)
            elif implementation['type'] == 'behavioral':
                return await self._deploy_behavioral_mimicry(strategy, threat_data)
            else:
                logger.warning(f"Unknown strategy implementation type: {implementation['type']}")
                return False
                
        except Exception as e:
            logger.error(f"Error deploying strategy {strategy.strategy_id}: {e}")
            return False
    
    async def _deploy_honeypot_strategy(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy adaptive honeypot strategy"""
        try:
            source_ip = threat_data.get('source_ip')
            threat_type = threat_data.get('type')
            
            # Determine what service to honeypot based on threat
            service_map = {
                'port_scan': ['ssh', 'http', 'ftp'],
                'service_enumeration': ['http', 'ftp', 'telnet'],
                'lateral_movement': ['ssh', 'smb'],
                'web_attack': ['http'],
                'default': ['ssh', 'http']
            }
            
            services = service_map.get(threat_type, service_map['default'])
            
            # Deploy honeypots for identified services
            deployed = 0
            for service in services:
                # Check if we already have enough of this service type
                existing_honeypots = await self._count_service_honeypots(service)
                if existing_honeypots < 2:  # Limit to 2 per service type
                    honeypot_id = await self.honeypot_manager.deploy_honeypot(
                        service, 
                        {'adaptive': True, 'threat_response': True}
                    )
                    if honeypot_id:
                        deployed += 1
                        logger.info(f"Deployed adaptive {service} honeypot: {honeypot_id}")
            
            return deployed > 0
            
        except Exception as e:
            logger.error(f"Error deploying honeypot strategy: {e}")
            return False
    
    async def _deploy_service_emulation(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy decoy service emulation"""
        try:
            # This would implement more sophisticated service emulation
            # For now, use existing honeypot infrastructure
            return await self._deploy_honeypot_strategy(strategy, threat_data)
            
        except Exception as e:
            logger.error(f"Error deploying service emulation: {e}")
            return False
    
    async def _deploy_network_deception(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy network topology deception"""
        try:
            # This would implement network-level deception
            # For now, simulate deployment
            logger.info("Deploying network topology deception (simulated)")
            await asyncio.sleep(0.1)  # Simulate deployment time
            return True
            
        except Exception as e:
            logger.error(f"Error deploying network deception: {e}")
            return False
    
    async def _deploy_data_breadcrumbs(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy deceptive data breadcrumbs"""
        try:
            # This would implement canary tokens and fake credentials
            # For now, simulate deployment
            logger.info("Deploying data breadcrumbs (simulated)")
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error deploying data breadcrumbs: {e}")
            return False
    
    async def _deploy_behavioral_mimicry(self, strategy: DeceptionStrategy, threat_data: Dict[str, Any]) -> bool:
        """Deploy behavioral mimicry"""
        try:
            # This would implement behavioral simulation
            # For now, simulate deployment
            logger.info("Deploying behavioral mimicry (simulated)")
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            logger.error(f"Error deploying behavioral mimicry: {e}")
            return False
    
    async def _count_service_honeypots(self, service_type: str) -> int:
        """Count existing honeypots of a specific service type"""
        try:
            status = self.honeypot_manager.get_honeypot_status()
            count = 0
            for honeypot_data in status['honeypots'].values():
                if honeypot_data['service_type'] == service_type and honeypot_data['status'] == 'running':
                    count += 1
            return count
        except:
            return 0
    
    def _calculate_success_probability(self, deployed_strategies: List[str]) -> float:
        """Calculate the probability of success for deployed strategies"""
        if not deployed_strategies:
            return 0.0
        
        # Simple calculation based on strategy effectiveness
        total_effectiveness = 0.0
        for strategy_id in deployed_strategies:
            if strategy_id in self.strategies:
                total_effectiveness += self.strategies[strategy_id].effectiveness_score
        
        # Average effectiveness, capped at 0.95
        return min(total_effectiveness / len(deployed_strategies), 0.95)
    
    async def adapt_to_new_threat(self, ioc_data: Dict[str, Any]):
        """Adapt deception strategies based on new threat intelligence"""
        try:
            ioc_type = ioc_data.get('type', 'unknown')
            threat_types = ioc_data.get('threat_types', [])
            
            logger.info(f"Adapting to new threat intelligence: {ioc_type}")
            
            # Update strategy effectiveness based on new intelligence
            for threat_type in threat_types:
                await self._update_strategy_effectiveness(threat_type, ioc_data)
            
            # Consider deploying preemptive deception
            if ioc_data.get('confidence', 0) > 0.8:
                await self._deploy_preemptive_deception(ioc_data)
            
        except Exception as e:
            logger.error(f"Error adapting to new threat: {e}")
    
    async def _update_strategy_effectiveness(self, threat_type: str, ioc_data: Dict[str, Any]):
        """Update strategy effectiveness based on threat intelligence"""
        try:
            for strategy in self.strategies.values():
                if threat_type in strategy.target_threats:
                    # Adjust effectiveness based on IOC confidence and recency
                    confidence = ioc_data.get('confidence', 0.5)
                    adjustment = (confidence - 0.5) * 0.1  # Small adjustment
                    
                    new_effectiveness = strategy.effectiveness_score + adjustment
                    strategy.effectiveness_score = max(0.1, min(new_effectiveness, 1.0))
                    
                    logger.debug(f"Updated {strategy.strategy_id} effectiveness to {strategy.effectiveness_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating strategy effectiveness: {e}")
    
    async def _deploy_preemptive_deception(self, ioc_data: Dict[str, Any]):
        """Deploy preemptive deception based on high-confidence intelligence"""
        try:
            # Create a synthetic threat event for preemptive response
            synthetic_threat = {
                'type': 'preemptive_response',
                'source_ip': 'unknown',
                'confidence': ioc_data.get('confidence', 0.8),
                'threat_types': ioc_data.get('threat_types', []),
                'id': f"preemptive_{int(datetime.utcnow().timestamp())}"
            }
            
            await self.respond_to_threat(synthetic_threat)
            
        except Exception as e:
            logger.error(f"Error deploying preemptive deception: {e}")
    
    async def learn_from_interaction(self, interaction_data: Dict[str, Any]):
        """Learn from honeypot interactions to improve strategies"""
        try:
            attacker_ip = interaction_data.get('source_ip')
            service = interaction_data.get('service')
            success = interaction_data.get('successful', False)
            
            # Track learning data
            if attacker_ip not in self.learning_data:
                self.learning_data[attacker_ip] = {
                    'interactions': 0,
                    'services_targeted': set(),
                    'success_rate': 0.0,
                    'techniques': set()
                }
            
            learning_entry = self.learning_data[attacker_ip]
            learning_entry['interactions'] += 1
            learning_entry['services_targeted'].add(service)
            
            # Update success rate
            if success:
                learning_entry['success_rate'] = (
                    learning_entry['success_rate'] * (learning_entry['interactions'] - 1) + 1.0
                ) / learning_entry['interactions']
            
            # Extract techniques from commands
            commands = interaction_data.get('commands', [])
            for command in commands:
                technique = self._classify_technique(command)
                if technique:
                    learning_entry['techniques'].add(technique)
            
            # Update strategy effectiveness based on learning
            await self._update_strategies_from_learning(attacker_ip, learning_entry)
            
        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
    
    def _classify_technique(self, command: str) -> Optional[str]:
        """Classify attack technique from command"""
        if not command:
            return None
        
        command = command.lower()
        
        # Simple technique classification
        if any(word in command for word in ['ls', 'dir', 'cat', 'type']):
            return 'discovery'
        elif any(word in command for word in ['wget', 'curl', 'download']):
            return 'download'
        elif any(word in command for word in ['nc', 'netcat', 'telnet']):
            return 'lateral_movement'
        elif any(word in command for word in ['ps', 'top', 'tasklist']):
            return 'process_discovery'
        elif any(word in command for word in ['chmod', 'chown', 'icacls']):
            return 'privilege_escalation'
        else:
            return 'unknown'
    
    async def _update_strategies_from_learning(self, attacker_ip: str, learning_data: Dict[str, Any]):
        """Update strategy effectiveness based on learning data"""
        try:
            # If attacker is showing sophisticated behavior, increase deception complexity
            if learning_data['interactions'] > 10 and len(learning_data['techniques']) > 3:
                # Increase effectiveness of behavioral mimicry and advanced strategies
                if 'behavioral_mimicry' in self.strategies:
                    self.strategies['behavioral_mimicry'].effectiveness_score = min(
                        self.strategies['behavioral_mimicry'].effectiveness_score + 0.05, 1.0
                    )
            
            # Track which services are most targeted
            targeted_services = learning_data['services_targeted']
            for service in targeted_services:
                # This could inform future honeypot deployment decisions
                pass
            
        except Exception as e:
            logger.error(f"Error updating strategies from learning: {e}")
    
    async def _monitor_strategy_effectiveness(self):
        """Monitor and evaluate strategy effectiveness"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                # Evaluate effectiveness of active responses
                current_time = datetime.utcnow()
                for threat_id, response in list(self.active_responses.items()):
                    # Check if response is old enough to evaluate
                    if (current_time - response.deployment_time).total_seconds() > 3600:
                        await self._evaluate_response_effectiveness(threat_id, response)
                
            except Exception as e:
                logger.error(f"Error monitoring strategy effectiveness: {e}")
    
    async def _evaluate_response_effectiveness(self, threat_id: str, response: DeceptionResponse):
        """Evaluate the effectiveness of a deception response"""
        try:
            # Check if the response attracted interactions
            # This is a simplified evaluation - a real implementation would be more sophisticated
            
            effectiveness_score = 0.0
            
            # Check honeypot interactions after deployment
            honeypot_status = self.honeypot_manager.get_honeypot_status()
            recent_interactions = 0
            
            for honeypot_data in honeypot_status['honeypots'].values():
                if honeypot_data['last_interaction']:
                    last_interaction = datetime.fromisoformat(honeypot_data['last_interaction'])
                    if last_interaction > response.deployment_time:
                        recent_interactions += 1
            
            if recent_interactions > 0:
                effectiveness_score = min(recent_interactions / 10.0, 1.0)
            
            # Update strategy performance tracking
            for strategy_id in response.strategies_deployed:
                if strategy_id not in self.strategy_performance:
                    self.strategy_performance[strategy_id] = []
                
                self.strategy_performance[strategy_id].append(effectiveness_score)
                
                # Keep only recent performance data
                if len(self.strategy_performance[strategy_id]) > 100:
                    self.strategy_performance[strategy_id] = self.strategy_performance[strategy_id][-100:]
            
            # Remove old response from active tracking
            if threat_id in self.active_responses:
                del self.active_responses[threat_id]
            
            logger.debug(f"Evaluated response {threat_id} effectiveness: {effectiveness_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error evaluating response effectiveness: {e}")
    
    async def _adaptive_strategy_updates(self):
        """Adaptively update strategies based on performance"""
        while True:
            try:
                await asyncio.sleep(7200)  # Update every 2 hours
                
                # Update strategy effectiveness based on performance data
                for strategy_id, performance_data in self.strategy_performance.items():
                    if len(performance_data) >= 5:  # Need minimum data for updates
                        avg_performance = sum(performance_data) / len(performance_data)
                        
                        if strategy_id in self.strategies:
                            strategy = self.strategies[strategy_id]
                            
                            # Adjust effectiveness score towards observed performance
                            adjustment = (avg_performance - strategy.effectiveness_score) * 0.1
                            strategy.effectiveness_score = max(0.1, min(
                                strategy.effectiveness_score + adjustment, 1.0
                            ))
                            
                            logger.debug(f"Updated {strategy_id} effectiveness to {strategy.effectiveness_score:.2f}")
                
            except Exception as e:
                logger.error(f"Error in adaptive strategy updates: {e}")
    
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get current status of deception strategies"""
        status = {
            'strategies': {},
            'active_responses': len(self.active_responses),
            'learning_data_points': len(self.learning_data),
            'performance_tracking': {}
        }
        
        # Strategy information
        for strategy_id, strategy in self.strategies.items():
            status['strategies'][strategy_id] = {
                'name': strategy.name,
                'effectiveness_score': strategy.effectiveness_score,
                'deployment_cost': strategy.deployment_cost,
                'target_threats': strategy.target_threats
            }
        
        # Performance tracking summary
        for strategy_id, performance_data in self.strategy_performance.items():
            if performance_data:
                status['performance_tracking'][strategy_id] = {
                    'deployments': len(performance_data),
                    'average_effectiveness': sum(performance_data) / len(performance_data),
                    'recent_trend': performance_data[-5:] if len(performance_data) >= 5 else performance_data
                }
        
        return status
