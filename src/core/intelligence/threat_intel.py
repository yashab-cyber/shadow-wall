"""
Threat Intelligence Management
Collects and processes threat intelligence from various sources
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import aiohttp
from pathlib import Path

from ...utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ThreatFeed:
    """Threat intelligence feed definition"""
    name: str
    url: str
    feed_type: str
    api_key: Optional[str]
    update_interval: int
    last_update: Optional[datetime]
    is_active: bool

class ThreatIntelligence:
    """Threat intelligence collection and management"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.feeds = self._initialize_feeds()
        self.ioc_database = {}
        self.running = False
        
        # Event callbacks
        self._ioc_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_iocs': 0,
            'active_feeds': 0,
            'last_update': None
        }
    
    def _initialize_feeds(self) -> List[ThreatFeed]:
        """Initialize threat intelligence feeds"""
        feeds = []
        
        for feed_config in self.config.get('feeds', []):
            feed = ThreatFeed(
                name=feed_config['name'],
                url=feed_config['url'],
                feed_type=feed_config.get('type', 'json'),
                api_key=feed_config.get('api_key'),
                update_interval=feed_config.get('update_interval', 3600),
                last_update=None,
                is_active=True
            )
            feeds.append(feed)
        
        return feeds
    
    async def start(self):
        """Start threat intelligence collection"""
        logger.info("Starting threat intelligence collection...")
        
        self.running = True
        
        # Start feed update tasks
        for feed in self.feeds:
            asyncio.create_task(self._update_feed_periodically(feed))
        
        # Start IOC cleanup task
        asyncio.create_task(self._cleanup_expired_iocs())
        
        logger.info("Threat intelligence collection started")
    
    async def stop(self):
        """Stop threat intelligence collection"""
        logger.info("Stopping threat intelligence collection...")
        self.running = False
    
    async def _update_feed_periodically(self, feed: ThreatFeed):
        """Periodically update a threat intelligence feed"""
        while self.running:
            try:
                if feed.is_active:
                    await self._update_feed(feed)
                
                await asyncio.sleep(feed.update_interval)
                
            except Exception as e:
                logger.error(f"Error updating feed {feed.name}: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def _update_feed(self, feed: ThreatFeed):
        """Update a single threat intelligence feed"""
        try:
            logger.info(f"Updating threat intelligence feed: {feed.name}")
            
            if feed.url.startswith('file://'):
                # Local file feed
                file_path = feed.url[7:]  # Remove 'file://' prefix
                await self._process_file_feed(feed, file_path)
            else:
                # Remote HTTP feed
                await self._process_http_feed(feed)
            
            feed.last_update = datetime.utcnow()
            self.stats['last_update'] = feed.last_update
            
            logger.info(f"Successfully updated feed: {feed.name}")
            
        except Exception as e:
            logger.error(f"Failed to update feed {feed.name}: {e}")
    
    async def _process_file_feed(self, feed: ThreatFeed, file_path: str):
        """Process a local file threat feed"""
        try:
            file_obj = Path(file_path)
            if not file_obj.exists():
                logger.warning(f"Feed file not found: {file_path}")
                return
            
            with open(file_obj, 'r') as f:
                if feed.feed_type == 'json':
                    data = json.load(f)
                else:
                    # Plain text, one IOC per line
                    data = {'iocs': [line.strip() for line in f if line.strip()]}
            
            await self._process_feed_data(feed, data)
            
        except Exception as e:
            logger.error(f"Error processing file feed {feed.name}: {e}")
    
    async def _process_http_feed(self, feed: ThreatFeed):
        """Process a remote HTTP threat feed"""
        try:
            headers = {}
            if feed.api_key:
                headers['Authorization'] = f"Bearer {feed.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(feed.url, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        if feed.feed_type == 'json':
                            data = await response.json()
                        else:
                            text_data = await response.text()
                            data = {'iocs': [line.strip() for line in text_data.split('\n') if line.strip()]}
                        
                        await self._process_feed_data(feed, data)
                    else:
                        logger.error(f"HTTP error {response.status} for feed {feed.name}")
        
        except Exception as e:
            logger.error(f"Error processing HTTP feed {feed.name}: {e}")
    
    async def _process_feed_data(self, feed: ThreatFeed, data: Dict[str, Any]):
        """Process threat intelligence data from a feed"""
        try:
            iocs = []
            
            # Extract IOCs based on feed format
            if 'iocs' in data:
                iocs = data['iocs']
            elif 'indicators' in data:
                iocs = data['indicators']
            elif isinstance(data, list):
                iocs = data
            else:
                logger.warning(f"Unknown data format in feed {feed.name}")
                return
            
            new_iocs = 0
            updated_iocs = 0
            
            for ioc_data in iocs:
                if isinstance(ioc_data, str):
                    # Simple string IOC
                    ioc_data = {
                        'value': ioc_data,
                        'type': self._guess_ioc_type(ioc_data),
                        'confidence': 0.5,
                        'source': feed.name
                    }
                
                ioc_id = self._generate_ioc_id(ioc_data)
                
                if ioc_id in self.ioc_database:
                    # Update existing IOC
                    existing_ioc = self.ioc_database[ioc_id]
                    existing_ioc['last_seen'] = datetime.utcnow()
                    existing_ioc['times_seen'] += 1
                    
                    # Update confidence if new data is more confident
                    new_confidence = ioc_data.get('confidence', 0.5)
                    if new_confidence > existing_ioc.get('confidence', 0.0):
                        existing_ioc['confidence'] = new_confidence
                    
                    updated_iocs += 1
                else:
                    # Add new IOC
                    new_ioc = {
                        'id': ioc_id,
                        'type': ioc_data.get('type', 'unknown'),
                        'value': ioc_data.get('value', ''),
                        'confidence': ioc_data.get('confidence', 0.5),
                        'source': ioc_data.get('source', feed.name),
                        'first_seen': datetime.utcnow(),
                        'last_seen': datetime.utcnow(),
                        'times_seen': 1,
                        'threat_types': ioc_data.get('threat_types', []),
                        'context': ioc_data.get('context', {}),
                        'expiry_date': self._calculate_expiry_date(ioc_data),
                        'is_active': True
                    }
                    
                    self.ioc_database[ioc_id] = new_ioc
                    new_iocs += 1
                    
                    # Notify callbacks about new IOC
                    await self._notify_new_ioc(new_ioc)
            
            self.stats['total_iocs'] = len(self.ioc_database)
            logger.info(f"Feed {feed.name}: {new_iocs} new IOCs, {updated_iocs} updated IOCs")
            
        except Exception as e:
            logger.error(f"Error processing feed data for {feed.name}: {e}")
    
    def _guess_ioc_type(self, value: str) -> str:
        """Guess the IOC type from its value"""
        import re
        
        # IP address
        if re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', value):
            return 'ip'
        
        # Domain
        if re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', value):
            return 'domain'
        
        # Hash (MD5, SHA1, SHA256)
        if re.match(r'^[a-fA-F0-9]{32}$', value):
            return 'md5'
        elif re.match(r'^[a-fA-F0-9]{40}$', value):
            return 'sha1'
        elif re.match(r'^[a-fA-F0-9]{64}$', value):
            return 'sha256'
        
        # URL
        if value.startswith(('http://', 'https://', 'ftp://')):
            return 'url'
        
        return 'unknown'
    
    def _generate_ioc_id(self, ioc_data: Dict[str, Any]) -> str:
        """Generate a unique ID for an IOC"""
        import hashlib
        
        ioc_type = ioc_data.get('type', 'unknown')
        value = ioc_data.get('value', '')
        
        # Create hash of type and value
        hash_input = f"{ioc_type}:{value}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:16]
    
    def _calculate_expiry_date(self, ioc_data: Dict[str, Any]) -> datetime:
        """Calculate expiry date for an IOC"""
        # Default expiry: 30 days from now
        default_expiry = datetime.utcnow() + timedelta(days=30)
        
        # Check if expiry is specified in the data
        if 'expiry_date' in ioc_data:
            try:
                return datetime.fromisoformat(ioc_data['expiry_date'])
            except:
                pass
        
        # Adjust based on IOC type and confidence
        confidence = ioc_data.get('confidence', 0.5)
        ioc_type = ioc_data.get('type', 'unknown')
        
        # High confidence IOCs last longer
        if confidence > 0.8:
            return datetime.utcnow() + timedelta(days=60)
        elif confidence < 0.3:
            return datetime.utcnow() + timedelta(days=7)
        
        return default_expiry
    
    async def _notify_new_ioc(self, ioc: Dict[str, Any]):
        """Notify callbacks about new IOC"""
        for callback in self._ioc_callbacks:
            try:
                await callback(ioc)
            except Exception as e:
                logger.error(f"Error in IOC callback: {e}")
    
    async def _cleanup_expired_iocs(self):
        """Clean up expired IOCs"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                current_time = datetime.utcnow()
                expired_iocs = []
                
                for ioc_id, ioc in self.ioc_database.items():
                    if ioc.get('expiry_date') and current_time > ioc['expiry_date']:
                        expired_iocs.append(ioc_id)
                
                # Remove expired IOCs
                for ioc_id in expired_iocs:
                    del self.ioc_database[ioc_id]
                
                if expired_iocs:
                    logger.info(f"Cleaned up {len(expired_iocs)} expired IOCs")
                    self.stats['total_iocs'] = len(self.ioc_database)
                
            except Exception as e:
                logger.error(f"Error cleaning up expired IOCs: {e}")
    
    def query_iocs(self, ioc_type: str = None, value: str = None, 
                   min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Query IOCs from the database"""
        results = []
        
        for ioc in self.ioc_database.values():
            if not ioc.get('is_active', True):
                continue
            
            if ioc_type and ioc.get('type') != ioc_type:
                continue
            
            if value and value not in ioc.get('value', ''):
                continue
            
            if ioc.get('confidence', 0.0) < min_confidence:
                continue
            
            results.append(ioc.copy())
        
        return results
    
    def check_ioc(self, value: str, ioc_type: str = None) -> Dict[str, Any]:
        """Check if a value is a known IOC"""
        for ioc in self.ioc_database.values():
            if not ioc.get('is_active', True):
                continue
            
            if ioc.get('value') == value:
                if ioc_type is None or ioc.get('type') == ioc_type:
                    return ioc.copy()
        
        return None
    
    def add_ioc(self, ioc_data: Dict[str, Any]) -> str:
        """Manually add an IOC to the database"""
        try:
            ioc_id = self._generate_ioc_id(ioc_data)
            
            new_ioc = {
                'id': ioc_id,
                'type': ioc_data.get('type', self._guess_ioc_type(ioc_data.get('value', ''))),
                'value': ioc_data.get('value', ''),
                'confidence': ioc_data.get('confidence', 0.8),  # Manual IOCs get higher confidence
                'source': ioc_data.get('source', 'manual'),
                'first_seen': datetime.utcnow(),
                'last_seen': datetime.utcnow(),
                'times_seen': 1,
                'threat_types': ioc_data.get('threat_types', []),
                'context': ioc_data.get('context', {}),
                'expiry_date': self._calculate_expiry_date(ioc_data),
                'is_active': True
            }
            
            self.ioc_database[ioc_id] = new_ioc
            self.stats['total_iocs'] = len(self.ioc_database)
            
            logger.info(f"Added manual IOC: {new_ioc['type']} - {new_ioc['value']}")
            
            return ioc_id
            
        except Exception as e:
            logger.error(f"Error adding manual IOC: {e}")
            return None
    
    def on_new_ioc(self, callback: Callable):
        """Register callback for new IOC events"""
        self._ioc_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        active_feeds = sum(1 for feed in self.feeds if feed.is_active)
        
        # IOC type distribution
        ioc_types = {}
        for ioc in self.ioc_database.values():
            ioc_type = ioc.get('type', 'unknown')
            ioc_types[ioc_type] = ioc_types.get(ioc_type, 0) + 1
        
        return {
            'total_iocs': len(self.ioc_database),
            'active_feeds': active_feeds,
            'total_feeds': len(self.feeds),
            'last_update': self.stats['last_update'].isoformat() if self.stats['last_update'] else None,
            'ioc_type_distribution': ioc_types,
            'feed_status': [
                {
                    'name': feed.name,
                    'is_active': feed.is_active,
                    'last_update': feed.last_update.isoformat() if feed.last_update else None
                }
                for feed in self.feeds
            ]
        }
