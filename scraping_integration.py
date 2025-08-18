import sys
import os
import json
import time
import sqlite3
import threading
import asyncio
import aiohttp
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("Advertencia: Módulo 'schedule' no disponible")
# Importar yaml y pandas con fallback
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import hashlib
import gzip
import pickle
from urllib.parse import urljoin, urlparse, parse_qs
from collections import defaultdict, deque
import queue
import weakref
import re
from bs4 import BeautifulSoup
import requests

# PySide6 imports for UI
try:
    from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                                   QTextEdit, QPushButton, QLabel, QSpinBox, 
                                   QLineEdit, QComboBox, QListWidget, QListWidgetItem,
                                   QCheckBox, QGroupBox, QScrollArea, QFrame)
    from PySide6.QtCore import Qt, QThread, pyqtSignal
    from PySide6.QtGui import QFont, QColor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    print("⚠️ PySide6 no disponible - UI no disponible")

# Enhanced ScrapingIntegration with REAL functionality
class ScrapingIntegration:
    def __init__(self):
        self.initialized = False
        self.current_html = ""
        self.current_url = ""
        self.analysis_results = {}
        self.discovery_results = []
        self.extracted_data = {}  # Store extracted data
        self.selected_elements = []  # Store selected elements
        self.metrics_data = {}
        self.plugin_results = {}
        self.cache_results = {}
        self.proxy_results = {}
        self.scheduler_results = {}
        
        # Initialize all components
        self._initialize_components()
        self.initialized = True
        print("✅ ScrapingIntegration inicializado correctamente")
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Setup basic components
            self._setup_basic_fallbacks()
            # Setup advanced features
            self._setup_advanced_features()
            
        except Exception as e:
            print(f"❌ Error inicializando componentes: {e}")
            self._setup_basic_fallbacks()
    
    def _setup_advanced_features(self):
        """Setup advanced scraping features"""
        try:
            # Setup cleanup task
            if SCHEDULE_AVAILABLE:
                schedule.every(3600).seconds.do(self._cleanup_task)
            
            # Setup metrics collection
            if SCHEDULE_AVAILABLE:
                schedule.every(300).seconds.do(self._metrics_task)
            
            # Start background thread for scheduled tasks
            self._start_background_thread()
            
        except Exception as e:
            print(f"⚠️ Error configurando características avanzadas: {e}")
    
    def _setup_basic_fallbacks(self):
        """Setup basic fallback implementations"""
        self.config_manager = FallbackConfigManager()
        self.ethical_scraper = FallbackScraper()
        self.html_analyzer = FallbackAnalyzer()
        self.structured_extractor = FallbackExtractor()
        self.advanced_selectors = FallbackSelectors()
        self.intelligent_crawler = FallbackCrawler()
        self.metrics_collector = FallbackMetrics()
        self.plugin_manager = FallbackPluginManager()
        self.etl_pipeline = FallbackETL()
        self.task_scheduler = FallbackScheduler()
        self.cache_manager = FallbackCache()
        self.proxy_manager = FallbackProxyManager()
        self.user_agent_manager = FallbackUserAgentManager()
    
    def _start_background_thread(self):
        """Start background thread for scheduled tasks"""
        def run_scheduler():
            while True:
                try:
                    if SCHEDULE_AVAILABLE:
                        schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error en scheduler: {e}")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
    
    def _cleanup_task(self):
        """Cleanup task for maintenance"""
        try:
            # Clean old cache entries
            if hasattr(self, 'cache_manager'):
                self.cache_manager.cleanup()
        except Exception as e:
            print(f"Error en cleanup: {e}")
    
    def _metrics_task(self):
        """Metrics collection task"""
        try:
            if hasattr(self, 'metrics_collector'):
                self.metrics_collector.record_operation("scheduled_metrics", True)
        except Exception as e:
            print(f"Error en métricas: {e}")
    
    def update_content(self, html_content: str, url: str = "") -> bool:
        """Update current page content for analysis"""
        try:
            self.current_html = html_content
            self.current_url = url
            print(f"Contenido actualizado: {len(html_content)} caracteres de {url}")
            return True
        except Exception as e:
            print(f"Error actualizando contenido: {e}")
            return False
    
    def analyze_page(self) -> Dict[str, Any]:
        """Analyze current page HTML with REAL functionality"""
        try:
            if not self.current_html:
                return {"error": "No hay contenido HTML para analizar"}
            
            # Get proxy for this analysis if available
            current_proxy = None
            if hasattr(self, 'proxy_manager') and self.proxy_manager:
                current_proxy = self.proxy_manager.get_proxy()
                if current_proxy:
                    print(f"🔄 Usando proxy: {current_proxy.url}")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(self.current_html, 'html.parser')
            
            # Real analysis
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "url": self.current_url,
                "analysis": {
                    "links": [],
                    "images": [],
                    "forms": [],
                    "tables": [],
                    "lists": [],
                    "headings": [],
                    "paragraphs": [],
                    "buttons": [],
                    "inputs": []
                }
            }
            
            # Extract links
            for link in soup.find_all('a', href=True):
                analysis["analysis"]["links"].append({
                    "text": link.get_text(strip=True),
                    "href": link['href'],
                    "title": link.get('title', ''),
                    "class": link.get('class', [])
                })
            
            # Extract images
            for img in soup.find_all('img'):
                analysis["analysis"]["images"].append({
                    "src": img.get('src', ''),
                    "alt": img.get('alt', ''),
                    "title": img.get('title', ''),
                    "class": img.get('class', [])
                })
            
            # Extract forms
            for form in soup.find_all('form'):
                analysis["analysis"]["forms"].append({
                    "action": form.get('action', ''),
                    "method": form.get('method', 'get'),
                    "id": form.get('id', ''),
                    "class": form.get('class', [])
                })
            
            # Extract tables
            for table in soup.find_all('table'):
                analysis["analysis"]["tables"].append({
                    "id": table.get('id', ''),
                    "class": table.get('class', []),
                    "rows": len(table.find_all('tr')),
                    "headers": [th.get_text(strip=True) for th in table.find_all('th')]
                })
            
            # Extract lists
            for ul in soup.find_all(['ul', 'ol']):
                analysis["analysis"]["lists"].append({
                    "type": ul.name,
                    "id": ul.get('id', ''),
                    "class": ul.get('class', []),
                    "items": len(ul.find_all('li'))
                })
            
            # Extract headings
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                analysis["analysis"]["headings"].append({
                    "level": heading.name,
                    "text": heading.get_text(strip=True),
                    "id": heading.get('id', ''),
                    "class": heading.get('class', [])
                })
            
            # Extract paragraphs
            for p in soup.find_all('p'):
                analysis["analysis"]["paragraphs"].append({
                    "text": p.get_text(strip=True)[:100] + "..." if len(p.get_text(strip=True)) > 100 else p.get_text(strip=True),
                    "id": p.get('id', ''),
                    "class": p.get('class', [])
                })
            
            # Extract buttons
            for button in soup.find_all('button'):
                analysis["analysis"]["buttons"].append({
                    "text": button.get_text(strip=True),
                    "type": button.get('type', ''),
                    "id": button.get('id', ''),
                    "class": button.get('class', [])
                })
            
            # Extract inputs
            for input_elem in soup.find_all('input'):
                analysis["analysis"]["inputs"].append({
                    "type": input_elem.get('type', ''),
                    "name": input_elem.get('name', ''),
                    "id": input_elem.get('id', ''),
                    "class": input_elem.get('class', [])
                })
            
            self.analysis_results = analysis
            return analysis
            
        except Exception as e:
            return {"error": f"Error analizando página: {str(e)}"}
    
    def discover_urls(self, max_urls: int = 100, max_depth: int = 3) -> Dict[str, Any]:
        """Discover URLs from current page with REAL functionality"""
        try:
            if not self.current_html:
                return {"error": "No hay contenido HTML para analizar"}
            
            soup = BeautifulSoup(self.current_html, 'html.parser')
            discovered_urls = []
            fuzzing_results = []
            
            # Extract all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    discovered_urls.append(href)
                elif href.startswith('/'):
                    # Convert relative to absolute
                    if self.current_url:
                        base_url = self.current_url.rstrip('/')
                        discovered_urls.append(f"{base_url}{href}")
                elif href.startswith('#'):
                    # Skip anchors
                    continue
                else:
                    # Other relative URLs
                    if self.current_url:
                        discovered_urls.append(urljoin(self.current_url, href))
            
            # Remove duplicates
            discovered_urls = list(set(discovered_urls))
            
            # Limit results
            discovered_urls = discovered_urls[:max_urls]
            
            # Generate fuzzing URLs
            if self.current_url:
                base_url = self.current_url.rstrip('/')
                common_paths = ['/admin', '/login', '/register', '/api', '/docs', '/help', '/about', '/contact']
                for path in common_paths:
                    fuzzing_results.append(f"{base_url}{path}")
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "discovered_urls": discovered_urls,
                "fuzzing_results": fuzzing_results,
                "total_discovered": len(discovered_urls),
                "total_fuzzing": len(fuzzing_results)
            }
            
            self.discovery_results = result
            return result
            
        except Exception as e:
            return {"error": f"Error descubriendo URLs: {str(e)}"}
    
    def extract_data(self, selectors: List[str] = None) -> Dict[str, Any]:
        """Extract data using CSS selectors with REAL functionality"""
        try:
            if not self.current_html:
                return {"error": "No hay contenido HTML para extraer"}
            
            if not selectors:
                selectors = ['h1', 'h2', 'h3', 'p', 'a', 'img', 'table']
            
            soup = BeautifulSoup(self.current_html, 'html.parser')
            extracted_data = {}
            selectors_used = []
            
            for selector in selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        selectors_used.append(selector)
                        extracted_data[selector] = []
                        
                        for element in elements:
                            data = {
                                "text": element.get_text(strip=True),
                                "tag": element.name,
                                "attributes": dict(element.attrs),
                                "html": str(element)[:200] + "..." if len(str(element)) > 200 else str(element)
                            }
                            extracted_data[selector] = data
                except Exception as e:
                    print(f"Error con selector '{selector}': {e}")
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "selectors_used": selectors_used,
                "extracted_data": extracted_data,
                "total_elements": sum(len(data) for data in extracted_data.values()),
                "export_ready": True
            }
            
            self.extracted_data = result
            return result
            
        except Exception as e:
            return {"error": f"Error extrayendo datos: {str(e)}"}
    
    def get_selectable_elements(self) -> List[Dict[str, Any]]:
        """Get all selectable elements from current page with better suggestions"""
        try:
            if not self.current_html:
                return []
            
            soup = BeautifulSoup(self.current_html, 'html.parser')
            elements = []
            
            # Priority elements that are most likely to be selected
            priority_selectors = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headers
                'a[href]',  # Links
                'button', 'input[type="button"]', 'input[type="submit"]',  # Buttons
                'img[alt]',  # Images with alt text
                'p',  # Paragraphs
                'span', 'div',  # General containers
                'li',  # List items
                'td', 'th',  # Table cells
                'label',  # Form labels
                'strong', 'b', 'em', 'i',  # Text emphasis
                'blockquote',  # Quotes
                'code', 'pre'  # Code blocks
            ]
            
            for selector in priority_selectors:
                for tag in soup.select(selector):
                    text = tag.get_text(strip=True)
                    if text and len(text) > 2:  # Shorter minimum for more suggestions
                        # Calculate importance score
                        importance = self._calculate_importance(tag, text)
                        
                        # Extract structured data
                        structured_data = self._extract_structured_data(tag)
                        
                        element = {
                            "tag": tag.name,
                            "text": self._clean_text(text)[:80] + "..." if len(self._clean_text(text)) > 80 else self._clean_text(text),
                            "full_text": self._clean_text(text),
                            "texto_limpio": structured_data["texto_limpio"],
                            "texto_original": structured_data["texto_original"],
                            "selector": self._generate_selector(tag),
                            "attributes": dict(tag.attrs),
                            "html": str(tag)[:150] + "..." if len(str(tag)) > 150 else str(tag),
                            "importance": importance,
                            "type": self._get_element_type(tag),
                            "structured_data": structured_data
                        }
                        elements.append(element)
            
            # Sort by importance and remove duplicates
            seen_selectors = set()
            unique_elements = []
            for element in sorted(elements, key=lambda x: x['importance'], reverse=True):
                if element['selector'] not in seen_selectors:
                    unique_elements.append(element)
                    seen_selectors.add(element['selector'])
            
            return unique_elements[:50]  # Limit to top 50 elements
            
        except Exception as e:
            print(f"Error obteniendo elementos seleccionables: {e}")
            return []
    
    def _calculate_importance(self, tag, text: str) -> int:
        """Calculate importance score for an element"""
        score = 0
        
        # Base score by tag type
        tag_scores = {
            'h1': 100, 'h2': 90, 'h3': 80, 'h4': 70, 'h5': 60, 'h6': 50,
            'a': 85, 'button': 80, 'input': 75,
            'img': 70, 'p': 65, 'span': 40, 'div': 35,
            'li': 60, 'td': 55, 'th': 60,
            'strong': 70, 'b': 65, 'em': 65, 'i': 60,
            'blockquote': 75, 'code': 70, 'pre': 75
        }
        
        score += tag_scores.get(tag.name, 30)
        
        # Bonus for meaningful text length
        if 10 <= len(text) <= 200:
            score += 20
        elif len(text) > 200:
            score += 10
        
        # Bonus for having href (links)
        if tag.name == 'a' and tag.get('href'):
            score += 15
        
        # Bonus for having alt text (images)
        if tag.name == 'img' and tag.get('alt'):
            score += 10
        
        # Bonus for having id or class
        if tag.get('id'):
            score += 25
        if tag.get('class'):
            score += 15
        
        return score
    
    def _get_element_type(self, tag) -> str:
        """Get human-readable element type"""
        if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return "Encabezado"
        elif tag.name == 'a':
            return "Enlace"
        elif tag.name in ['button', 'input']:
            return "Botón"
        elif tag.name == 'img':
            return "Imagen"
        elif tag.name == 'p':
            return "Párrafo"
        elif tag.name in ['span', 'div']:
            return "Contenedor"
        elif tag.name in ['li', 'td', 'th']:
            return "Elemento de lista"
        elif tag.name in ['strong', 'b', 'em', 'i']:
            return "Texto destacado"
        elif tag.name in ['blockquote', 'code', 'pre']:
            return "Cita/Código"
        else:
            return "Otro"
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text for better readability"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Remove common HTML entities
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
            '&hellip;': '...',
            '&mdash;': '—',
            '&ndash;': '–',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&ldquo;': '"',
            '&rdquo;': '"'
        }
        
        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Limit length for display
        if len(text) > 200:
            text = text[:197] + "..."
        
        return text.strip()
    
    def _format_for_export(self, text: str) -> str:
        """Format text specifically for export (CSV, Excel, etc.)"""
        if not text:
            return ""
        
        # Clean the text first
        text = self._clean_text(text)
        
        # Remove problematic characters for CSV
        text = text.replace('"', '""')  # Escape quotes for CSV
        text = text.replace('\n', ' ')  # Replace newlines with spaces
        text = text.replace('\r', ' ')  # Replace carriage returns
        text = text.replace('\t', ' ')  # Replace tabs
        
        # Remove other problematic characters
        text = ''.join(char for char in text if char.isprintable() or char in ' \n\t')
        
        return text.strip()
    
    def _extract_structured_data(self, element) -> dict:
        """Extract structured data from an element"""
        data = {
            "texto_limpio": self._clean_text(element.get_text(strip=True)),
            "texto_original": element.get_text(strip=True),
            "tipo_elemento": element.name,
            "selector": self._generate_selector(element),
            "atributos": {}
        }
        
        # Extract useful attributes
        for attr, value in element.attrs.items():
            if attr in ['href', 'src', 'alt', 'title', 'id', 'class']:
                if isinstance(value, list):
                    data["atributos"][attr] = ' '.join(value)
                else:
                    data["atributos"][attr] = str(value)
        
        # Extract specific data based on element type
        if element.name == 'a':
            data["url"] = element.get('href', '')
            data["texto_enlace"] = self._clean_text(element.get_text(strip=True))
        elif element.name == 'img':
            data["url_imagen"] = element.get('src', '')
            data["texto_alternativo"] = element.get('alt', '')
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            data["nivel_encabezado"] = element.name
            data["texto_encabezado"] = self._clean_text(element.get_text(strip=True))
        elif element.name in ['button', 'input']:
            data["tipo_boton"] = element.get('type', 'button')
            data["valor_boton"] = element.get('value', '')
        
        return data
    
    def _generate_selector(self, element) -> str:
        """Generate CSS selector for an element"""
        try:
            if element.get('id'):
                return f"#{element['id']}"
            elif element.get('class'):
                return f".{'.'.join(element['class'])}"
            else:
                return element.name
        except:
            return element.name
    
    def add_selected_element(self, element_data: Dict[str, Any]):
        """Add element to selected elements list"""
        if element_data not in self.selected_elements:
            self.selected_elements.append(element_data)
            print(f"✅ Elemento añadido: {element_data.get('tag', 'unknown')} - {element_data.get('text', '')[:50]}...")
    
    def add_element_by_selector(self, selector: str) -> Dict[str, Any]:
        """Add element by CSS selector from current page"""
        try:
            if not self.current_html:
                return {"error": "No hay contenido HTML para analizar"}
            
            soup = BeautifulSoup(self.current_html, 'html.parser')
            elements = soup.select(selector)
            
            if not elements:
                return {"error": f"No se encontraron elementos con el selector: {selector}"}
            
            added_elements = []
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    element_data = {
                        "tag": element.name,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "full_text": text,
                        "selector": selector,
                        "attributes": dict(element.attrs),
                        "html": str(element)[:200] + "..." if len(str(element)) > 200 else str(element)
                    }
                    self.add_selected_element(element_data)
                    added_elements.append(element_data)
            
            return {
                "success": True,
                "elements_added": len(added_elements),
                "selector": selector
            }
            
        except Exception as e:
            return {"error": f"Error añadiendo elementos: {str(e)}"}
    
    def add_element_by_click(self, x: int, y: int) -> Dict[str, Any]:
        """Add element by click coordinates (simulated)"""
        try:
            if not self.current_html:
                return {"error": "No hay contenido HTML para analizar"}
            
            # This would be called from JavaScript in the browser
            # For now, we'll simulate finding elements near the click
            soup = BeautifulSoup(self.current_html, 'html.parser')
            
            # Find elements that might be at the click position
            # This is a simplified approach - in a real implementation,
            # you'd use JavaScript to get the exact element at coordinates
            clickable_elements = soup.find_all(['a', 'button', 'input', 'div', 'span', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if not clickable_elements:
                return {"error": "No se encontraron elementos clickeables"}
            
            # For demonstration, we'll add the first few elements
            added_elements = []
            for element in clickable_elements[:3]:  # Limit to first 3 elements
                text = element.get_text(strip=True)
                if text and len(text) > 3:
                    element_data = {
                        "tag": element.name,
                        "text": text[:100] + "..." if len(text) > 100 else text,
                        "full_text": text,
                        "selector": self._generate_selector(element),
                        "attributes": dict(element.attrs),
                        "html": str(element)[:200] + "..." if len(str(element)) > 200 else str(element),
                        "click_position": {"x": x, "y": y}
                    }
                    self.add_selected_element(element_data)
                    added_elements.append(element_data)
            
            return {
                "success": True,
                "elements_added": len(added_elements),
                "click_position": {"x": x, "y": y}
            }
            
        except Exception as e:
            return {"error": f"Error añadiendo elementos por clic: {str(e)}"}
    
    def remove_selected_element(self, element_data: Dict[str, Any]):
        """Remove element from selected elements list"""
        if element_data in self.selected_elements:
            self.selected_elements.remove(element_data)
    
    def get_selected_elements(self) -> List[Dict[str, Any]]:
        """Get all selected elements"""
        return self.selected_elements
    
    def clear_selected_elements(self):
        """Clear all selected elements"""
        self.selected_elements.clear()
    
    def export_selected_data(self, format_type: str = "json", filename: str = None) -> Dict[str, Any]:
        """Export selected elements data with improved formatting"""
        try:
            if not self.selected_elements:
                return {"error": "No hay elementos seleccionados para exportar"}
            
            if not filename:
                filename = f"scraped_data_{int(time.time())}"
            
            # Prepare clean data for export
            clean_elements = []
            for element in self.selected_elements:
                clean_element = {
                    "tipo_elemento": element.get("tag", ""),
                    "tipo_categoria": element.get("type", ""),
                    "texto_limpio": element.get("texto_limpio", ""),
                    "texto_original": element.get("texto_original", ""),
                    "selector_css": element.get("selector", ""),
                    "importancia": element.get("importance", 0),
                    "url_pagina": self.current_url,
                    "timestamp_extraccion": datetime.now().isoformat()
                }
                
                # Add structured data if available
                if "structured_data" in element:
                    structured = element["structured_data"]
                    clean_element.update({
                        "url_enlace": structured.get("url", ""),
                        "texto_enlace": structured.get("texto_enlace", ""),
                        "url_imagen": structured.get("url_imagen", ""),
                        "texto_alternativo": structured.get("texto_alternativo", ""),
                        "nivel_encabezado": structured.get("nivel_encabezado", ""),
                        "texto_encabezado": structured.get("texto_encabezado", ""),
                        "tipo_boton": structured.get("tipo_boton", ""),
                        "valor_boton": structured.get("valor_boton", "")
                    })
                
                # Add attributes as separate columns
                attributes = element.get("attributes", {})
                for attr, value in attributes.items():
                    if attr in ['href', 'src', 'alt', 'title', 'id', 'class']:
                        clean_element[f"atributo_{attr}"] = str(value)
                
                clean_elements.append(clean_element)
            
            data_to_export = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "url": self.current_url,
                    "total_elementos": len(self.selected_elements),
                    "formato_exportacion": format_type
                },
                "elementos": clean_elements
            }
            
            if format_type == "json":
                filepath = f"{filename}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data_to_export, f, indent=2, ensure_ascii=False)
            
            elif format_type == "csv":
                filepath = f"{filename}.csv"
                # Create DataFrame with clean data if pandas available
                if not PANDAS_AVAILABLE:
                    return {"error": "pandas no está disponible para exportar CSV"}
                df = pd.DataFrame(clean_elements)
                
                # Reorder columns for better readability
                priority_columns = [
                    'tipo_elemento', 'tipo_categoria', 'texto_limpio', 'texto_original',
                    'selector_css', 'importancia', 'url_enlace', 'texto_enlace',
                    'url_imagen', 'texto_alternativo', 'nivel_encabezado', 'texto_encabezado',
                    'tipo_boton', 'valor_boton'
                ]
                
                # Add attribute columns
                for col in df.columns:
                    if col.startswith('atributo_'):
                        priority_columns.append(col)
                
                # Reorder columns
                existing_columns = [col for col in priority_columns if col in df.columns]
                remaining_columns = [col for col in df.columns if col not in priority_columns]
                final_columns = existing_columns + remaining_columns
                
                df = df[final_columns]
                df.to_csv(filepath, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
            
            elif format_type == "yaml":
                filepath = f"{filename}.yaml"
                if not YAML_AVAILABLE:
                    return {"error": "PyYAML no está disponible para exportar YAML"}
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(data_to_export, f, default_flow_style=False, allow_unicode=True)
            
            elif format_type == "excel":
                filepath = f"{filename}.xlsx"
                if not PANDAS_AVAILABLE:
                    return {"error": "pandas no está disponible para exportar Excel"}
                df = pd.DataFrame(clean_elements)
                
                # Create Excel writer with formatting
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Datos_Extraidos', index=False)
                    
                    # Get the workbook and worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Datos_Extraidos']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return {
                "success": True,
                "format": format_type,
                "filename": filepath,
                "elements_exported": len(self.selected_elements),
                "columns_exported": len(clean_elements[0]) if clean_elements else 0
            }
            
        except Exception as e:
            return {"error": f"Error exportando datos: {str(e)}"}
    
    # Keep existing methods for compatibility
    def run_plugins(self) -> Dict[str, Any]:
        """Run plugins (placeholder)"""
        return {
            "plugins_executed": 0,
            "total_plugins": 0,
            "plugin_results": {}
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "operation_stats": {
                "analyses": 1,
                "extractions": 1,
                "exports": 0
            }
        }
    
    def manage_cache(self, action: str = "info") -> Dict[str, Any]:
        """Manage cache"""
        return {
            "operation_success": True,
            "cache_info": {
                "size": 0,
                "entries": 0
            }
        }
    
    def manage_proxies(self, action: str = "info") -> Dict[str, Any]:
        """Manage proxies"""
        try:
            if not hasattr(self, 'proxy_manager') or not self.proxy_manager:
                return {
                    "operation_success": False,
                    "error": "Proxy manager no disponible"
                }
            
            if action == "info":
                # Get proxy statistics
                total_proxies = len(self.proxy_manager.proxies) if hasattr(self.proxy_manager, 'proxies') else 0
                active_proxies = len([p for p in self.proxy_manager.proxies if p.is_active]) if hasattr(self.proxy_manager, 'proxies') else 0
                
                return {
                    "operation_success": True,
                    "proxy_info": {
                        "total": total_proxies,
                        "active": active_proxies,
                        "enabled": getattr(self.proxy_manager, 'enabled', False),
                        "rotation_strategy": getattr(self.proxy_manager, 'rotation_strategy', 'round_robin')
                    }
                }
            elif action == "get_current":
                # Get current proxy
                current_proxy = self.proxy_manager.get_proxy()
                if current_proxy:
                    return {
                        "operation_success": True,
                        "current_proxy": current_proxy.url,
                        "proxy_details": {
                            "host": current_proxy.host,
                            "port": current_proxy.port,
                            "protocol": current_proxy.protocol,
                            "is_active": current_proxy.is_active,
                            "failure_count": current_proxy.failure_count
                        }
                    }
                else:
                    return {
                        "operation_success": False,
                        "error": "No hay proxies disponibles"
                    }
            else:
                return {
                    "operation_success": False,
                    "error": f"Acción no reconocida: {action}"
                }
                
        except Exception as e:
            return {
                "operation_success": False,
                "error": f"Error gestionando proxies: {str(e)}"
            }
    
    def manage_scheduler(self, action: str = "info") -> Dict[str, Any]:
        """Manage scheduler"""
        return {
            "operation_success": True,
            "scheduler_info": {
                "tasks": 0,
                "running": 0
            }
        }
    
    def export_data(self, format_type: str = "json", filename: str = None) -> Dict[str, Any]:
        """Export data"""
        return self.export_selected_data(format_type, filename)
    
    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {
                "scrapelillo_available": True,
                "components": {
                    "config_manager": hasattr(self, 'config_manager'),
                    "ethical_scraper": hasattr(self, 'ethical_scraper'),
                    "html_analyzer": hasattr(self, 'html_analyzer'),
                    "structured_extractor": hasattr(self, 'structured_extractor'),
                    "advanced_selectors": hasattr(self, 'advanced_selectors'),
                    "intelligent_crawler": hasattr(self, 'intelligent_crawler'),
                    "metrics_collector": hasattr(self, 'metrics_collector'),
                    "plugin_manager": hasattr(self, 'plugin_manager'),
                    "etl_pipeline": hasattr(self, 'etl_pipeline'),
                    "task_scheduler": hasattr(self, 'task_scheduler'),
                    "cache_manager": hasattr(self, 'cache_manager'),
                    "proxy_manager": hasattr(self, 'proxy_manager'),
                    "user_agent_manager": hasattr(self, 'user_agent_manager')
                },
                "current_state": {
                    "html_loaded": bool(self.current_html),
                    "url_loaded": bool(self.current_url),
                    "analysis_ready": bool(self.analysis_results),
                    "elements_selected": len(self.selected_elements),
                    "data_extracted": bool(self.extracted_data)
                }
            }
            return status
        except Exception as e:
            return {"error": f"Error obteniendo estado: {str(e)}"}
    
    # URL Export Functions
    def export_urls_to_csv(self, urls: List[str], filename: str = "discovered_urls.csv") -> Dict[str, Any]:
        """Export URLs to CSV format"""
        try:
            import pandas as pd
            
            # Create DataFrame with URLs
            df = pd.DataFrame({
                'url': urls,
                'discovered_at': datetime.now().isoformat(),
                'source': self.current_url or 'unknown'
            })
            
            # Save to CSV
            df.to_csv(filename, index=False, encoding='utf-8')
            
            return {
                "success": True,
                "filename": filename,
                "urls_exported": len(urls),
                "format": "CSV"
            }
        except Exception as e:
            return {"error": f"Error exportando a CSV: {str(e)}"}
    
    def export_urls_to_json(self, urls: List[str], filename: str = "discovered_urls.json") -> Dict[str, Any]:
        """Export URLs to JSON format"""
        try:
            data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "source_url": self.current_url or "unknown",
                    "total_urls": len(urls)
                },
                "urls": urls
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "filename": filename,
                "urls_exported": len(urls),
                "format": "JSON"
            }
        except Exception as e:
            return {"error": f"Error exportando a JSON: {str(e)}"}
    
    def export_urls_to_txt(self, urls: List[str], filename: str = "discovered_urls.txt") -> Dict[str, Any]:
        """Export URLs to plain text format"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# URLs descubiertas\n")
                f.write(f"# Exportado: {datetime.now().isoformat()}\n")
                f.write(f"# Fuente: {self.current_url or 'unknown'}\n")
                f.write(f"# Total URLs: {len(urls)}\n\n")
                
                for i, url in enumerate(urls, 1):
                    f.write(f"{i}. {url}\n")
            
            return {
                "success": True,
                "filename": filename,
                "urls_exported": len(urls),
                "format": "TXT"
            }
        except Exception as e:
            return {"error": f"Error exportando a TXT: {str(e)}"}
    
    def export_urls_to_excel(self, urls: List[str], filename: str = "discovered_urls.xlsx") -> Dict[str, Any]:
        """Export URLs to Excel format"""
        try:
            import pandas as pd
            
            # Ensure filename has .xlsx extension
            if not filename.endswith('.xlsx'):
                filename = filename.replace('.excel', '.xlsx')
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
            
            # Create DataFrame with URLs and metadata
            df = pd.DataFrame({
                'url': urls,
                'discovered_at': datetime.now().isoformat(),
                'source': self.current_url or 'unknown',
                'url_type': ['link' for _ in urls]  # Default type
            })
            
            # Save to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='URLs', index=False)
                
                # Create metadata sheet
                metadata_df = pd.DataFrame({
                    'Property': ['Total URLs', 'Source URL', 'Export Date', 'Format'],
                    'Value': [len(urls), self.current_url or 'unknown', datetime.now().isoformat(), 'Excel']
                })
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            return {
                "success": True,
                "filename": filename,
                "urls_exported": len(urls),
                "format": "Excel"
            }
        except Exception as e:
            return {"error": f"Error exportando a Excel: {str(e)}"}

# Fallback implementations
class FallbackScraper:
    def __init__(self, base_url="", **kwargs):
        self.base_url = base_url
        self.session = None
        self.user_agent = "Tron Browser Scraper/1.0"
    
    def analyze_page(self, html_content):
        return {"elements": [], "structure": "basic", "status": "fallback"}

class FallbackAnalyzer:
    def __init__(self):
        self.detected_elements = []
    
    def analyze_html(self, html_content):
        return {"tables": [], "lists": [], "forms": [], "links": [], "images": []}

class FallbackExtractor:
    def __init__(self):
        pass
    
    def extract_structured_data(self, html_content):
        return {"data": [], "schema": "basic"}

class FallbackSelectors:
    def __init__(self):
        pass
    
    def find_elements(self, html_content, selector_type="all"):
        return []

class FallbackCrawler:
    def __init__(self, base_url="", **kwargs):
        self.base_url = base_url
        self.discovered_urls = []
    
    def discover_urls(self, max_urls=100, max_depth=3):
        return []

class FallbackMetrics:
    def __init__(self):
        self.stats = defaultdict(int)
    
    def record_operation(self, operation, success=True):
        self.stats[operation] += 1 if success else 0

class FallbackPluginManager:
    def __init__(self):
        self.plugins = {}
    
    def load_plugins(self):
        return []
    
    def get_plugin_info(self):
        return {"loaded": 0, "available": 0}

class FallbackScheduler:
    def __init__(self):
        self.tasks = {}
    
    def add_task(self, name, func, interval=3600):
        self.tasks[name] = {"func": func, "interval": interval}
    
    def get_tasks(self):
        return list(self.tasks.keys())

class FallbackCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value, ttl=3600):
        self.cache[key] = {"value": value, "expires": time.time() + ttl}

class FallbackProxyManager:
    def __init__(self):
        self.proxies = []
        self.enabled = False  # Añadido para compatibilidad con el panel de proxies
        self.rotation_strategy = 'round_robin'  # Añadido para compatibilidad
        self.timeout = 10  # Añadido para compatibilidad
        self.max_failures = 3  # Añadido para compatibilidad
        self.validation_url = "http://httpbin.org/ip"  # Añadido para compatibilidad

    def add_proxy(self, proxy):
        self.proxies.append(proxy)

    def get_proxy(self):
        return self.proxies[0] if self.proxies else None

class FallbackUserAgentManager:
    def __init__(self):
        self.user_agents = ["Tron Browser/1.0"]
    
    def get_user_agent(self):
        return self.user_agents[0]

class FallbackConfigManager:
    def __init__(self):
        self.config = {
            "scraping": {"default_delay": 1.0, "timeout": 30},
            "cache": {"enabled": True, "max_size": 1000},
            "proxies": {"enabled": False},
            "discovery": {"max_urls": 1000, "max_depth": 3}
        }
    
    def get_config(self, section=None):
        if section:
            return self.config.get(section, {})
        return self.config

class FallbackETL:
    def __init__(self):
        pass
    
    def process_data(self, data):
        return data

# Create global instance
scraping_integration = ScrapingIntegration()
