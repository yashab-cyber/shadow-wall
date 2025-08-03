"""
Network Traffic Monitor
Real-time network packet capture and analysis
"""

import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import json

try:
    from scapy.all import AsyncSniffer, Packet, IP, TCP, UDP, ARP
    from scapy.layers.inet import ICMP
except ImportError:
    # Fallback for environments without scapy
    class AsyncSniffer:
        def __init__(self, *args, **kwargs):
            pass
        def start(self): pass
        def stop(self): pass

import psutil
from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class NetworkPacket:
    """Network packet data structure"""
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: str
    size: int
    flags: Dict[str, Any]
    payload_preview: str

@dataclass
class ConnectionEvent:
    """Network connection event"""
    timestamp: datetime
    event_type: str  # 'connection', 'disconnection', 'data_transfer'
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: str
    bytes_transferred: int
    connection_duration: Optional[float]

class NetworkMonitor:
    """Real-time network traffic monitor"""
    
    def __init__(self, interfaces: List[str], config: Dict[str, Any]):
        self.interfaces = interfaces
        self.config = config
        self.running = False
        self.sniffers = {}
        self.connection_tracker = {}
        
        # Event callbacks
        self._packet_callbacks: List[Callable] = []
        self._connection_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'packets_captured': 0,
            'connections_tracked': 0,
            'suspicious_activities': 0
        }
    
    async def start(self):
        """Start network monitoring"""
        logger.info(f"Starting network monitoring on interfaces: {self.interfaces}")
        
        self.running = True
        
        # Start packet capture on each interface
        for interface in self.interfaces:
            try:
                await self._start_interface_monitoring(interface)
            except Exception as e:
                logger.error(f"Failed to start monitoring on {interface}: {e}")
        
        # Start connection tracking
        asyncio.create_task(self._track_connections())
        
        # Start periodic statistics reporting
        asyncio.create_task(self._report_statistics())
    
    async def stop(self):
        """Stop network monitoring"""
        logger.info("Stopping network monitoring...")
        self.running = False
        
        # Stop all sniffers
        for interface, sniffer in self.sniffers.items():
            try:
                sniffer.stop()
                logger.info(f"Stopped monitoring on {interface}")
            except Exception as e:
                logger.error(f"Error stopping sniffer on {interface}: {e}")
    
    async def _start_interface_monitoring(self, interface: str):
        """Start monitoring on a specific interface"""
        try:
            # Create packet filter based on configuration
            packet_filter = self._build_packet_filter()
            
            # Start async sniffer
            sniffer = AsyncSniffer(
                iface=interface,
                filter=packet_filter,
                prn=lambda pkt: asyncio.create_task(self._process_packet(pkt, interface)),
                store=False  # Don't store packets in memory
            )
            
            sniffer.start()
            self.sniffers[interface] = sniffer
            
            logger.info(f"Started packet capture on {interface}")
            
        except Exception as e:
            logger.error(f"Failed to start sniffer on {interface}: {e}")
            raise
    
    def _build_packet_filter(self) -> str:
        """Build BPF filter for packet capture"""
        # Basic filter to capture relevant traffic
        filters = [
            "tcp",  # TCP traffic
            "udp",  # UDP traffic
            "icmp", # ICMP traffic
            "arp"   # ARP traffic
        ]
        
        return " or ".join(filters)
    
    async def _process_packet(self, packet: Packet, interface: str):
        """Process captured packet"""
        try:
            # Extract packet information
            packet_data = self._extract_packet_data(packet, interface)
            
            if packet_data:
                # Update statistics
                self.stats['packets_captured'] += 1
                
                # Check for suspicious patterns
                await self._analyze_packet_for_threats(packet_data)
                
                # Notify callbacks
                for callback in self._packet_callbacks:
                    try:
                        await callback(packet_data)
                    except Exception as e:
                        logger.error(f"Error in packet callback: {e}")
        
        except Exception as e:
            logger.error(f"Error processing packet: {e}")
    
    def _extract_packet_data(self, packet: Packet, interface: str) -> Optional[NetworkPacket]:
        """Extract relevant data from packet"""
        try:
            if not packet.haslayer(IP):
                return None
            
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = ip_layer.proto
            
            src_port = None
            dst_port = None
            flags = {}
            
            # Extract transport layer information
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                protocol_name = "TCP"
                
                # Extract TCP flags
                flags.update({
                    'syn': bool(tcp_layer.flags.S),
                    'ack': bool(tcp_layer.flags.A),
                    'fin': bool(tcp_layer.flags.F),
                    'rst': bool(tcp_layer.flags.R),
                    'psh': bool(tcp_layer.flags.P),
                    'urg': bool(tcp_layer.flags.U)
                })
                
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                protocol_name = "UDP"
                
            elif packet.haslayer(ICMP):
                protocol_name = "ICMP"
                flags['type'] = packet[ICMP].type
                flags['code'] = packet[ICMP].code
                
            elif packet.haslayer(ARP):
                protocol_name = "ARP"
                flags['op'] = packet[ARP].op
                
            else:
                protocol_name = f"IP-{protocol}"
            
            # Extract payload preview (first 100 bytes)
            payload_preview = ""
            if hasattr(packet, 'payload'):
                raw_payload = bytes(packet.payload)[:100]
                payload_preview = raw_payload.hex()
            
            return NetworkPacket(
                timestamp=datetime.utcnow(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol_name,
                size=len(packet),
                flags=flags,
                payload_preview=payload_preview
            )
            
        except Exception as e:
            logger.error(f"Error extracting packet data: {e}")
            return None
    
    async def _analyze_packet_for_threats(self, packet_data: NetworkPacket):
        """Analyze packet for potential threats"""
        suspicious = False
        
        # Check for port scanning
        if packet_data.protocol == "TCP" and packet_data.flags.get('syn') and not packet_data.flags.get('ack'):
            # Potential SYN scan
            suspicious = True
        
        # Check for unusual port numbers
        if packet_data.dst_port and packet_data.dst_port > 65000:
            suspicious = True
        
        # Check for ARP spoofing attempts
        if packet_data.protocol == "ARP":
            suspicious = True
        
        if suspicious:
            self.stats['suspicious_activities'] += 1
            logger.warning(f"Suspicious packet detected: {packet_data.src_ip} -> {packet_data.dst_ip}:{packet_data.dst_port}")
    
    async def _track_connections(self):
        """Track network connections using system information"""
        while self.running:
            try:
                # Get current connections
                connections = psutil.net_connections(kind='inet')
                
                for conn in connections:
                    if conn.status == 'ESTABLISHED':
                        await self._process_connection(conn)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error tracking connections: {e}")
                await asyncio.sleep(10)
    
    async def _process_connection(self, connection):
        """Process a network connection"""
        try:
            if not connection.laddr or not connection.raddr:
                return
            
            connection_key = f"{connection.laddr.ip}:{connection.laddr.port}-{connection.raddr.ip}:{connection.raddr.port}"
            
            if connection_key not in self.connection_tracker:
                # New connection
                self.connection_tracker[connection_key] = {
                    'start_time': datetime.utcnow(),
                    'bytes_sent': 0,
                    'bytes_received': 0,
                    'pid': connection.pid
                }
                
                self.stats['connections_tracked'] += 1
                
                # Create connection event
                conn_event = ConnectionEvent(
                    timestamp=datetime.utcnow(),
                    event_type='connection',
                    src_ip=connection.laddr.ip,
                    dst_ip=connection.raddr.ip,
                    src_port=connection.laddr.port,
                    dst_port=connection.raddr.port,
                    protocol='TCP',
                    bytes_transferred=0,
                    connection_duration=None
                )
                
                # Notify callbacks
                for callback in self._connection_callbacks:
                    try:
                        await callback(conn_event)
                    except Exception as e:
                        logger.error(f"Error in connection callback: {e}")
        
        except Exception as e:
            logger.error(f"Error processing connection: {e}")
    
    async def _report_statistics(self):
        """Periodically report monitoring statistics"""
        while self.running:
            try:
                logger.info(f"Network monitoring stats: {json.dumps(self.stats, indent=2)}")
                await asyncio.sleep(60)  # Report every minute
            except Exception as e:
                logger.error(f"Error reporting statistics: {e}")
                await asyncio.sleep(60)
    
    def on_packet_captured(self, callback: Callable):
        """Register callback for packet capture events"""
        self._packet_callbacks.append(callback)
    
    def on_connection_event(self, callback: Callable):
        """Register callback for connection events"""
        self._connection_callbacks.append(callback)
    
    async def health_check(self):
        """Health check for network monitor"""
        if not self.running:
            raise Exception("Network monitor is not running")
        
        # Check if sniffers are still active
        for interface, sniffer in self.sniffers.items():
            if not hasattr(sniffer, 'running') or not sniffer.running:
                raise Exception(f"Sniffer on {interface} is not running")
        
        return True
