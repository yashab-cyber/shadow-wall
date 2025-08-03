"""
Sandbox Emulator
Provides a testing environment for security researchers and red teams
"""

import asyncio
import docker
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import tempfile
import shutil
from pathlib import Path

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class SandboxSession:
    """Sandbox session information"""
    session_id: str
    user_id: str
    environment_type: str
    status: str
    created_at: datetime
    expires_at: datetime
    resources: Dict[str, Any]
    access_info: Dict[str, Any]

class SandboxEmulator:
    """Security testing sandbox environment"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions: Dict[str, SandboxSession] = {}
        self.docker_client = None
        self.running = False
        
        # Available environments
        self.environments = {
            'basic_network': {
                'description': 'Basic network environment with vulnerable services',
                'services': ['web', 'ssh', 'ftp'],
                'network_size': 24
            },
            'corporate_sim': {
                'description': 'Simulated corporate network environment',
                'services': ['web', 'ssh', 'database', 'file_server', 'email'],
                'network_size': 16
            },
            'iot_environment': {
                'description': 'IoT device simulation environment',
                'services': ['http', 'telnet', 'upnp', 'mqtt'],
                'network_size': 28
            },
            'cloud_infrastructure': {
                'description': 'Cloud infrastructure simulation',
                'services': ['web', 'api', 'database', 'storage'],
                'network_size': 20
            }
        }
    
    async def start(self):
        """Start the sandbox emulator"""
        logger.info("Starting sandbox emulator...")
        
        if not self.config['enabled']:
            logger.info("Sandbox is disabled in configuration")
            return
        
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()
            
            # Test Docker connectivity
            self.docker_client.ping()
            
            self.running = True
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_sessions())
            
            logger.info("Sandbox emulator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start sandbox emulator: {e}")
            logger.info("Sandbox will run in simulation mode")
            self.running = True  # Run in simulation mode
    
    async def stop(self):
        """Stop the sandbox emulator"""
        logger.info("Stopping sandbox emulator...")
        
        self.running = False
        
        # Stop all active sessions
        for session_id in list(self.sessions.keys()):
            await self.destroy_session(session_id)
        
        if self.docker_client:
            self.docker_client.close()
        
        logger.info("Sandbox emulator stopped")
    
    async def create_session(self, user_id: str, environment_type: str, 
                           duration_minutes: int = 60) -> Optional[str]:
        """Create a new sandbox session"""
        try:
            # Check session limits
            active_sessions = sum(1 for s in self.sessions.values() if s.status == 'active')
            if active_sessions >= self.config['max_concurrent_sessions']:
                logger.warning(f"Maximum concurrent sessions reached: {active_sessions}")
                return None
            
            # Validate environment type
            if environment_type not in self.environments:
                logger.error(f"Unknown environment type: {environment_type}")
                return None
            
            # Generate session ID
            session_id = f"sandbox_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            # Calculate expiry time
            expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            # Create session
            session = SandboxSession(
                session_id=session_id,
                user_id=user_id,
                environment_type=environment_type,
                status='creating',
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                resources={},
                access_info={}
            )
            
            self.sessions[session_id] = session
            
            # Deploy the environment
            success = await self._deploy_environment(session)
            
            if success:
                session.status = 'active'
                logger.info(f"Created sandbox session {session_id} for user {user_id}")
                return session_id
            else:
                # Clean up failed session
                del self.sessions[session_id]
                return None
                
        except Exception as e:
            logger.error(f"Error creating sandbox session: {e}")
            return None
    
    async def _deploy_environment(self, session: SandboxSession) -> bool:
        """Deploy the sandbox environment"""
        try:
            environment = self.environments[session.environment_type]
            
            if self.docker_client:
                # Real Docker deployment
                return await self._deploy_docker_environment(session, environment)
            else:
                # Simulation mode
                return await self._simulate_environment_deployment(session, environment)
                
        except Exception as e:
            logger.error(f"Error deploying environment for session {session.session_id}: {e}")
            return False
    
    async def _deploy_docker_environment(self, session: SandboxSession, 
                                       environment: Dict[str, Any]) -> bool:
        """Deploy environment using Docker containers"""
        try:
            containers = []
            network_name = f"sandbox_{session.session_id}"
            
            # Create dedicated network
            network = self.docker_client.networks.create(
                network_name,
                driver="bridge",
                options={"com.docker.network.bridge.name": network_name}
            )
            
            # Deploy service containers
            for service in environment['services']:
                container_name = f"{session.session_id}_{service}"
                image = self._get_service_image(service)
                
                if image:
                    container = self.docker_client.containers.run(
                        image,
                        name=container_name,
                        network=network_name,
                        detach=True,
                        remove=True,
                        environment={"SANDBOX_SESSION": session.session_id}
                    )
                    containers.append(container)
            
            # Store deployment information
            session.resources = {
                'network': network_name,
                'containers': [c.name for c in containers],
                'services': environment['services']
            }
            
            # Generate access information
            session.access_info = {
                'network_range': f"172.{hash(session.session_id) % 255}.0.0/{environment['network_size']}",
                'services': {
                    service: f"{service}.{network_name}" 
                    for service in environment['services']
                },
                'access_methods': ['docker exec', 'network tools'],
                'documentation': f"Sandbox environment: {environment['description']}"
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying Docker environment: {e}")
            return False
    
    async def _simulate_environment_deployment(self, session: SandboxSession, 
                                             environment: Dict[str, Any]) -> bool:
        """Simulate environment deployment (when Docker is not available)"""
        try:
            # Simulate deployment delay
            await asyncio.sleep(2)
            
            # Generate simulated resources
            session.resources = {
                'simulation': True,
                'services': environment['services'],
                'network_size': environment['network_size']
            }
            
            # Generate simulated access information
            session.access_info = {
                'network_range': f"192.168.{hash(session.session_id) % 255}.0/{environment['network_size']}",
                'services': {
                    service: f"192.168.{hash(session.session_id) % 255}.{i+10}"
                    for i, service in enumerate(environment['services'])
                },
                'access_methods': ['simulated'],
                'documentation': f"Simulated sandbox: {environment['description']}",
                'note': 'This is a simulated environment for demonstration purposes'
            }
            
            logger.info(f"Simulated environment deployment for session {session.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error simulating environment deployment: {e}")
            return False
    
    def _get_service_image(self, service: str) -> Optional[str]:
        """Get Docker image for a service"""
        service_images = {
            'web': 'nginx:alpine',
            'ssh': 'linuxserver/openssh-server',
            'ftp': 'stilliard/pure-ftpd',
            'database': 'mysql:8.0',
            'file_server': 'dperson/samba',
            'email': 'mailserver/docker-mailserver',
            'api': 'node:alpine',
            'storage': 'minio/minio',
            'telnet': 'alpine:latest',
            'mqtt': 'eclipse-mosquitto',
            'upnp': 'alpine:latest'
        }
        
        return service_images.get(service)
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a sandbox session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Calculate remaining time
        remaining_time = (session.expires_at - datetime.utcnow()).total_seconds()
        
        return {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'environment_type': session.environment_type,
            'status': session.status,
            'created_at': session.created_at.isoformat(),
            'expires_at': session.expires_at.isoformat(),
            'remaining_time_minutes': max(0, remaining_time / 60),
            'resources': session.resources,
            'access_info': session.access_info,
            'environment_description': self.environments[session.environment_type]['description']
        }
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy a sandbox session"""
        try:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            # Clean up resources
            if self.docker_client and not session.resources.get('simulation'):
                await self._cleanup_docker_resources(session)
            
            # Remove session
            del self.sessions[session_id]
            
            logger.info(f"Destroyed sandbox session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error destroying session {session_id}: {e}")
            return False
    
    async def _cleanup_docker_resources(self, session: SandboxSession):
        """Clean up Docker resources for a session"""
        try:
            resources = session.resources
            
            # Stop and remove containers
            if 'containers' in resources:
                for container_name in resources['containers']:
                    try:
                        container = self.docker_client.containers.get(container_name)
                        container.stop(timeout=10)
                        container.remove()
                    except docker.errors.NotFound:
                        pass  # Container already removed
                    except Exception as e:
                        logger.warning(f"Error removing container {container_name}: {e}")
            
            # Remove network
            if 'network' in resources:
                try:
                    network = self.docker_client.networks.get(resources['network'])
                    network.remove()
                except docker.errors.NotFound:
                    pass  # Network already removed
                except Exception as e:
                    logger.warning(f"Error removing network {resources['network']}: {e}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up Docker resources: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sandbox sessions"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if current_time > session.expires_at:
                        expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    await self.destroy_session(session_id)
                    logger.info(f"Cleaned up expired session: {session_id}")
                
            except Exception as e:
                logger.error(f"Error during session cleanup: {e}")
    
    async def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List sandbox sessions"""
        sessions = []
        
        for session in self.sessions.values():
            if user_id is None or session.user_id == user_id:
                session_info = await self.get_session_info(session.session_id)
                if session_info:
                    sessions.append(session_info)
        
        return sessions
    
    def get_available_environments(self) -> Dict[str, Any]:
        """Get list of available sandbox environments"""
        return self.environments.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sandbox usage statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s.status == 'active')
        
        # Environment usage
        env_usage = {}
        for session in self.sessions.values():
            env_type = session.environment_type
            env_usage[env_type] = env_usage.get(env_type, 0) + 1
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': active_sessions,
            'max_sessions': self.config['max_concurrent_sessions'],
            'environment_usage': env_usage,
            'docker_available': self.docker_client is not None,
            'available_environments': list(self.environments.keys())
        }
