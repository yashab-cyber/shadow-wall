"""
Dynamic Honeypot Management System
Deploys and manages adaptive honeypots that learn from attacker behavior
"""

import asyncio
import logging
import random
import socket
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import subprocess
import threading
from pathlib import Path

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class HoneypotInstance:
    """Honeypot instance information"""
    instance_id: str
    service_type: str
    port: int
    ip_address: str
    status: str  # 'running', 'stopped', 'error'
    interactions: int
    last_interaction: Optional[datetime]
    created_at: datetime
    config: Dict[str, Any]

@dataclass
class HoneypotInteraction:
    """Honeypot interaction event"""
    timestamp: datetime
    honeypot_id: str
    source_ip: str
    source_port: int
    service: str
    interaction_type: str
    duration: float
    commands: List[str]
    payloads: List[str]
    session_data: Dict[str, Any]

class ServiceEmulator:
    """Base class for service emulators"""
    
    def __init__(self, port: int, config: Dict[str, Any]):
        self.port = port
        self.config = config
        self.running = False
        self.server = None
        self.interactions = []
        
    async def start(self):
        """Start the service emulator"""
        raise NotImplementedError
    
    async def stop(self):
        """Stop the service emulator"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
    
    async def handle_client(self, reader, writer):
        """Handle client connection"""
        raise NotImplementedError

class SSHHoneypot(ServiceEmulator):
    """SSH service emulator"""
    
    async def start(self):
        """Start SSH honeypot"""
        self.running = True
        self.server = await asyncio.start_server(
            self.handle_client, 
            '0.0.0.0', 
            self.port
        )
        logger.info(f"SSH honeypot started on port {self.port}")
    
    async def handle_client(self, reader, writer):
        """Handle SSH client connection"""
        client_ip = writer.get_extra_info('peername')[0]
        start_time = datetime.utcnow()
        
        try:
            # Send SSH banner
            banner = b"SSH-2.0-OpenSSH_7.4\r\n"
            writer.write(banner)
            await writer.drain()
            
            # Read client banner
            client_banner = await reader.readline()
            
            # Simulate authentication process
            commands = []
            payloads = []
            
            # Send some fake responses
            fake_responses = [
                b"login: ",
                b"Password: ",
                b"Permission denied, please try again.\r\n",
                b"Connection closed.\r\n"
            ]
            
            for response in fake_responses:
                writer.write(response)
                await writer.drain()
                
                # Try to read client input
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
                    if data:
                        commands.append(data.decode('utf-8', errors='ignore').strip())
                        payloads.append(data.hex())
                except asyncio.TimeoutError:
                    break
                except:
                    break
            
            # Create interaction record
            interaction = HoneypotInteraction(
                timestamp=start_time,
                honeypot_id=f"ssh_{self.port}",
                source_ip=client_ip,
                source_port=writer.get_extra_info('peername')[1],
                service="ssh",
                interaction_type="authentication_attempt",
                duration=(datetime.utcnow() - start_time).total_seconds(),
                commands=commands,
                payloads=payloads,
                session_data={
                    "client_banner": client_banner.decode('utf-8', errors='ignore').strip(),
                    "successful": False
                }
            )
            
            self.interactions.append(interaction)
            
        except Exception as e:
            logger.error(f"Error handling SSH client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

class HTTPHoneypot(ServiceEmulator):
    """HTTP service emulator"""
    
    async def start(self):
        """Start HTTP honeypot"""
        self.running = True
        self.server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            self.port
        )
        logger.info(f"HTTP honeypot started on port {self.port}")
    
    async def handle_client(self, reader, writer):
        """Handle HTTP client connection"""
        client_ip = writer.get_extra_info('peername')[0]
        start_time = datetime.utcnow()
        
        try:
            # Read HTTP request
            request_data = await reader.read(4096)
            request = request_data.decode('utf-8', errors='ignore')
            
            # Parse basic request info
            lines = request.split('\n')
            request_line = lines[0] if lines else ""
            
            # Generate fake response
            response_pages = [
                self._generate_login_page(),
                self._generate_admin_page(),
                self._generate_error_page(),
                self._generate_default_page()
            ]
            
            response_content = random.choice(response_pages)
            
            http_response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(response_content)}\r\n"
                "Server: Apache/2.4.41\r\n"
                "\r\n"
            ).encode() + response_content.encode()
            
            writer.write(http_response)
            await writer.drain()
            
            # Create interaction record
            interaction = HoneypotInteraction(
                timestamp=start_time,
                honeypot_id=f"http_{self.port}",
                source_ip=client_ip,
                source_port=writer.get_extra_info('peername')[1],
                service="http",
                interaction_type="web_request",
                duration=(datetime.utcnow() - start_time).total_seconds(),
                commands=[request_line],
                payloads=[request_data.hex()],
                session_data={
                    "request": request,
                    "user_agent": self._extract_user_agent(request),
                    "method": request_line.split()[0] if request_line.split() else "UNKNOWN"
                }
            )
            
            self.interactions.append(interaction)
            
        except Exception as e:
            logger.error(f"Error handling HTTP client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    def _generate_login_page(self) -> str:
        """Generate fake login page"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Admin Login</title></head>
        <body>
        <h2>Administrator Login</h2>
        <form method="post">
        <input type="text" name="username" placeholder="Username"><br>
        <input type="password" name="password" placeholder="Password"><br>
        <input type="submit" value="Login">
        </form>
        </body>
        </html>
        """
    
    def _generate_admin_page(self) -> str:
        """Generate fake admin page"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>System Administration</title></head>
        <body>
        <h1>System Control Panel</h1>
        <p>Welcome to the administration interface</p>
        <ul>
        <li><a href="/users">User Management</a></li>
        <li><a href="/config">Configuration</a></li>
        <li><a href="/logs">System Logs</a></li>
        </ul>
        </body>
        </html>
        """
    
    def _generate_error_page(self) -> str:
        """Generate fake error page"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Error 404</title></head>
        <body>
        <h1>404 - Not Found</h1>
        <p>The requested resource was not found on this server.</p>
        </body>
        </html>
        """
    
    def _generate_default_page(self) -> str:
        """Generate fake default page"""
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Welcome</title></head>
        <body>
        <h1>Welcome to our server</h1>
        <p>This is the default page for this web server.</p>
        </body>
        </html>
        """
    
    def _extract_user_agent(self, request: str) -> str:
        """Extract User-Agent from HTTP request"""
        lines = request.split('\n')
        for line in lines:
            if line.lower().startswith('user-agent:'):
                return line.split(':', 1)[1].strip()
        return "Unknown"

class FTPHoneypot(ServiceEmulator):
    """FTP service emulator"""
    
    async def start(self):
        """Start FTP honeypot"""
        self.running = True
        self.server = await asyncio.start_server(
            self.handle_client,
            '0.0.0.0',
            self.port
        )
        logger.info(f"FTP honeypot started on port {self.port}")
    
    async def handle_client(self, reader, writer):
        """Handle FTP client connection"""
        client_ip = writer.get_extra_info('peername')[0]
        start_time = datetime.utcnow()
        
        try:
            # Send FTP welcome message
            welcome = b"220 Welcome to FTP server\r\n"
            writer.write(welcome)
            await writer.drain()
            
            commands = []
            
            # Handle FTP commands
            while self.running:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=30.0)
                    if not data:
                        break
                    
                    command = data.decode('utf-8', errors='ignore').strip()
                    commands.append(command)
                    
                    # Respond to common FTP commands
                    if command.upper().startswith('USER'):
                        response = b"331 Password required\r\n"
                    elif command.upper().startswith('PASS'):
                        response = b"530 Login incorrect\r\n"
                    elif command.upper().startswith('QUIT'):
                        response = b"221 Goodbye\r\n"
                        writer.write(response)
                        await writer.drain()
                        break
                    else:
                        response = b"500 Command not understood\r\n"
                    
                    writer.write(response)
                    await writer.drain()
                    
                except asyncio.TimeoutError:
                    break
                except:
                    break
            
            # Create interaction record
            interaction = HoneypotInteraction(
                timestamp=start_time,
                honeypot_id=f"ftp_{self.port}",
                source_ip=client_ip,
                source_port=writer.get_extra_info('peername')[1],
                service="ftp",
                interaction_type="ftp_session",
                duration=(datetime.utcnow() - start_time).total_seconds(),
                commands=commands,
                payloads=[],
                session_data={"successful_login": False}
            )
            
            self.interactions.append(interaction)
            
        except Exception as e:
            logger.error(f"Error handling FTP client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

class HoneypotManager:
    """Manager for dynamic honeypot deployment and management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.honeypots: Dict[str, HoneypotInstance] = {}
        self.service_emulators: Dict[str, ServiceEmulator] = {}
        self.running = False
        
        # Available service types
        self.available_services = {
            'ssh': SSHHoneypot,
            'http': HTTPHoneypot,
            'ftp': FTPHoneypot,
            'telnet': self._create_telnet_emulator,
            'smtp': self._create_smtp_emulator
        }
        
        # Port ranges for different services
        self.port_ranges = {
            'ssh': (2200, 2299),
            'http': (8000, 8099),
            'ftp': (2100, 2199),
            'telnet': (2300, 2399),
            'smtp': (2500, 2599)
        }
        
        # Event callbacks
        self._interaction_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'honeypots_deployed': 0,
            'total_interactions': 0,
            'unique_attackers': set(),
            'most_targeted_service': None
        }
    
    async def start(self):
        """Start honeypot management"""
        logger.info("Starting honeypot management system...")
        
        self.running = True
        
        # Deploy initial honeypots
        if self.config['enabled']:
            await self._deploy_initial_honeypots()
        
        # Start background tasks
        asyncio.create_task(self._monitor_honeypots())
        asyncio.create_task(self._adaptive_deployment())
        asyncio.create_task(self._collect_interactions())
        
        logger.info("Honeypot management system started")
    
    async def stop(self):
        """Stop all honeypots"""
        logger.info("Stopping honeypot management system...")
        
        self.running = False
        
        # Stop all honeypots
        for honeypot_id in list(self.honeypots.keys()):
            await self.stop_honeypot(honeypot_id)
        
        logger.info("Honeypot management system stopped")
    
    async def _deploy_initial_honeypots(self):
        """Deploy initial set of honeypots"""
        for service in self.config['services']:
            try:
                await self.deploy_honeypot(service)
            except Exception as e:
                logger.error(f"Failed to deploy initial {service} honeypot: {e}")
    
    async def deploy_honeypot(self, service_type: str, custom_config: Optional[Dict] = None) -> str:
        """Deploy a new honeypot instance"""
        try:
            # Check if we've reached the maximum number of instances
            if len(self.honeypots) >= self.config['max_instances']:
                logger.warning("Maximum honeypot instances reached")
                return None
            
            # Find available port
            port = await self._find_available_port(service_type)
            if not port:
                logger.error(f"No available ports for {service_type} honeypot")
                return None
            
            # Generate unique instance ID
            instance_id = f"{service_type}_{port}_{int(datetime.utcnow().timestamp())}"
            
            # Create service emulator
            if service_type in self.available_services:
                if callable(self.available_services[service_type]):
                    emulator_class = self.available_services[service_type]
                    if service_type in ['ssh', 'http', 'ftp']:
                        emulator = emulator_class(port, custom_config or {})
                    else:
                        emulator = await emulator_class(port, custom_config or {})
                else:
                    emulator = await self.available_services[service_type](port, custom_config or {})
                
                # Start the emulator
                await emulator.start()
                
                # Create honeypot instance record
                honeypot = HoneypotInstance(
                    instance_id=instance_id,
                    service_type=service_type,
                    port=port,
                    ip_address="0.0.0.0",
                    status="running",
                    interactions=0,
                    last_interaction=None,
                    created_at=datetime.utcnow(),
                    config=custom_config or {}
                )
                
                self.honeypots[instance_id] = honeypot
                self.service_emulators[instance_id] = emulator
                
                self.stats['honeypots_deployed'] += 1
                
                logger.info(f"Deployed {service_type} honeypot on port {port} (ID: {instance_id})")
                
                return instance_id
            
            else:
                logger.error(f"Unknown service type: {service_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error deploying {service_type} honeypot: {e}")
            return None
    
    async def stop_honeypot(self, instance_id: str):
        """Stop a specific honeypot instance"""
        try:
            if instance_id in self.honeypots:
                # Stop the service emulator
                if instance_id in self.service_emulators:
                    await self.service_emulators[instance_id].stop()
                    del self.service_emulators[instance_id]
                
                # Update honeypot status
                self.honeypots[instance_id].status = "stopped"
                
                logger.info(f"Stopped honeypot {instance_id}")
            
        except Exception as e:
            logger.error(f"Error stopping honeypot {instance_id}: {e}")
    
    async def _find_available_port(self, service_type: str) -> Optional[int]:
        """Find an available port for the service type"""
        if service_type not in self.port_ranges:
            return None
        
        start_port, end_port = self.port_ranges[service_type]
        
        for port in range(start_port, end_port + 1):
            if await self._is_port_available(port):
                return port
        
        return None
    
    async def _is_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            # Check if any honeypot is already using this port
            for honeypot in self.honeypots.values():
                if honeypot.port == port and honeypot.status == "running":
                    return False
            
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.bind(('0.0.0.0', port))
            sock.close()
            return True
            
        except:
            return False
    
    async def _monitor_honeypots(self):
        """Monitor honeypot health and performance"""
        while self.running:
            try:
                for instance_id, honeypot in self.honeypots.items():
                    if honeypot.status == "running":
                        # Check if emulator is still running
                        if instance_id not in self.service_emulators:
                            honeypot.status = "error"
                            logger.warning(f"Honeypot {instance_id} emulator not found")
                            continue
                        
                        emulator = self.service_emulators[instance_id]
                        if not emulator.running:
                            honeypot.status = "stopped"
                            logger.warning(f"Honeypot {instance_id} stopped unexpectedly")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error monitoring honeypots: {e}")
                await asyncio.sleep(60)
    
    async def _adaptive_deployment(self):
        """Adaptively deploy honeypots based on attack patterns"""
        if not self.config.get('adaptive', {}).get('enabled', True):
            return
        
        while self.running:
            try:
                await asyncio.sleep(self.config['adaptive']['update_frequency'])
                
                # Analyze attack patterns
                attack_analysis = await self._analyze_attack_patterns()
                
                # Deploy honeypots for emerging threats
                await self._deploy_adaptive_honeypots(attack_analysis)
                
            except Exception as e:
                logger.error(f"Error in adaptive deployment: {e}")
    
    async def _analyze_attack_patterns(self) -> Dict[str, Any]:
        """Analyze recent attack patterns"""
        analysis = {
            'most_targeted_services': {},
            'attack_sources': {},
            'time_patterns': {},
            'emerging_threats': []
        }
        
        try:
            # Collect interactions from all honeypots
            all_interactions = []
            for emulator in self.service_emulators.values():
                all_interactions.extend(emulator.interactions)
            
            # Analyze service targeting
            service_counts = {}
            for interaction in all_interactions:
                service = interaction.service
                service_counts[service] = service_counts.get(service, 0) + 1
            
            analysis['most_targeted_services'] = service_counts
            
            # Update statistics
            if service_counts:
                self.stats['most_targeted_service'] = max(service_counts, key=service_counts.get)
            
            # Analyze attack sources
            source_counts = {}
            for interaction in all_interactions:
                source = interaction.source_ip
                source_counts[source] = source_counts.get(source, 0) + 1
                self.stats['unique_attackers'].add(source)
            
            analysis['attack_sources'] = source_counts
            
            self.stats['total_interactions'] = len(all_interactions)
            
        except Exception as e:
            logger.error(f"Error analyzing attack patterns: {e}")
        
        return analysis
    
    async def _deploy_adaptive_honeypots(self, analysis: Dict[str, Any]):
        """Deploy honeypots based on analysis"""
        try:
            # Deploy additional honeypots for highly targeted services
            for service, count in analysis['most_targeted_services'].items():
                if count > 10:  # If service is heavily targeted
                    # Count existing honeypots of this type
                    existing = sum(1 for h in self.honeypots.values() 
                                 if h.service_type == service and h.status == "running")
                    
                    if existing < 3:  # Deploy up to 3 instances per service
                        instance_id = await self.deploy_honeypot(service)
                        if instance_id:
                            logger.info(f"Adaptively deployed {service} honeypot due to high targeting")
            
        except Exception as e:
            logger.error(f"Error in adaptive honeypot deployment: {e}")
    
    async def _collect_interactions(self):
        """Collect and process honeypot interactions"""
        while self.running:
            try:
                for instance_id, emulator in self.service_emulators.items():
                    if emulator.interactions:
                        # Process new interactions
                        for interaction in emulator.interactions:
                            await self._process_interaction(interaction)
                        
                        # Update honeypot statistics
                        honeypot = self.honeypots[instance_id]
                        honeypot.interactions += len(emulator.interactions)
                        honeypot.last_interaction = max(
                            (i.timestamp for i in emulator.interactions),
                            default=honeypot.last_interaction
                        )
                        
                        # Clear processed interactions
                        emulator.interactions.clear()
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Error collecting interactions: {e}")
                await asyncio.sleep(10)
    
    async def _process_interaction(self, interaction: HoneypotInteraction):
        """Process a honeypot interaction"""
        try:
            logger.info(f"Honeypot interaction: {interaction.service} from {interaction.source_ip}")
            
            # Notify callbacks
            for callback in self._interaction_callbacks:
                try:
                    await callback(interaction.__dict__)
                except Exception as e:
                    logger.error(f"Error in interaction callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing interaction: {e}")
    
    # Simple implementations for other service emulators
    async def _create_telnet_emulator(self, port: int, config: Dict[str, Any]):
        """Create simple telnet emulator"""
        # This would implement a basic telnet honeypot
        return ServiceEmulator(port, config)
    
    async def _create_smtp_emulator(self, port: int, config: Dict[str, Any]):
        """Create simple SMTP emulator"""
        # This would implement a basic SMTP honeypot
        return ServiceEmulator(port, config)
    
    def get_honeypot_status(self) -> Dict[str, Any]:
        """Get status of all honeypots"""
        status = {
            'total_honeypots': len(self.honeypots),
            'running_honeypots': sum(1 for h in self.honeypots.values() if h.status == "running"),
            'total_interactions': sum(h.interactions for h in self.honeypots.values()),
            'honeypots': {
                instance_id: {
                    'service_type': h.service_type,
                    'port': h.port,
                    'status': h.status,
                    'interactions': h.interactions,
                    'last_interaction': h.last_interaction.isoformat() if h.last_interaction else None,
                    'uptime': (datetime.utcnow() - h.created_at).total_seconds()
                }
                for instance_id, h in self.honeypots.items()
            },
            'statistics': self.stats.copy()
        }
        
        # Convert set to list for JSON serialization
        status['statistics']['unique_attackers'] = len(status['statistics']['unique_attackers'])
        
        return status
    
    def on_interaction(self, callback: Callable):
        """Register callback for honeypot interactions"""
        self._interaction_callbacks.append(callback)
    
    async def health_check(self):
        """Health check for honeypot manager"""
        if not self.running:
            raise Exception("Honeypot manager is not running")
        
        # Check if we have active honeypots
        active_honeypots = sum(1 for h in self.honeypots.values() if h.status == "running")
        if active_honeypots == 0:
            logger.warning("No active honeypots running")
        
        return True
