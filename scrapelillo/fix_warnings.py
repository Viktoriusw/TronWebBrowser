#!/usr/bin/env python3
"""
Fix Warnings for Scrapelillo Project

Este script corrige automáticamente las advertencias detectadas en el proyecto.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any

class WarningFixer:
    """Corrector automático de advertencias"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        
    def fix_all_warnings(self):
        """Aplica todas las correcciones de advertencias"""
        logger.info("🔧 Aplicando correcciones de advertencias...")
        
        # Corregir imports faltantes
        self.fix_missing_imports()
        
        # Corregir logging
        self.fix_logging_issues()
        
        # Corregir excepciones genéricas
        self.fix_generic_exceptions()
        
        # Corregir print statements
        self.fix_print_statements()
        
        # Corregir requirements.txt
        self.fix_requirements()
        
        logger.info(f"✅ Aplicadas {len(self.fixes_applied)} correcciones")
        return self.fixes_applied
    
    def fix_missing_imports(self):
        """Corrige imports faltantes"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar si necesita imports específicos
                needed_imports = []
                
                if 'BeautifulSoup' in content and 'from bs4 import BeautifulSoup' not in content:
                    needed_imports.append('from bs4 import BeautifulSoup')
                
                if 'requests' in content and 'import requests' not in content:
                    needed_imports.append('import requests')
                
                if 'json' in content and 'import json' not in content:
                    needed_imports.append('import json')
                
                if 'yaml' in content and 'import yaml' not in content:
                    needed_imports.append('import yaml')
                
                if 'pandas' in content and 'import pandas' not in content:
                    needed_imports.append('import pandas as pd')
                
                if 'tkinter' in content and 'import tkinter' not in content:
                    needed_imports.append('import tkinter as tk')
                
                if 'threading' in content and 'import threading' not in content:
                    needed_imports.append('import threading')
                
                if 'asyncio' in content and 'import asyncio' not in content:
                    needed_imports.append('import asyncio')
                
                if 'aiohttp' in content and 'import aiohttp' not in content:
                    needed_imports.append('import aiohttp')
                
                if 'playwright' in content and 'from playwright' not in content:
                    needed_imports.append('from playwright.async_api import async_playwright')
                
                if 'sqlalchemy' in content and 'from sqlalchemy' not in content:
                    needed_imports.append('from sqlalchemy import create_engine')
                
                if 'pytest' in content and 'import pytest' not in content:
                    needed_imports.append('import pytest')
                
                # Añadir imports si es necesario
                if needed_imports:
                    # Encontrar la línea después de los imports existentes
                    lines = content.split('\n')
                    import_end = 0
                    
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            import_end = i + 1
                        elif line.strip() and not line.strip().startswith('#'):
                            break
                    
                    # Insertar nuevos imports
                    for import_stmt in needed_imports:
                        if import_stmt not in content:
                            lines.insert(import_end, import_stmt)
                            import_end += 1
                    
                    # Escribir archivo corregido
                    new_content = '\n'.join(lines)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixes_applied.append(f"Añadidos imports en {file_path}: {', '.join(needed_imports)}")
                    
            except Exception as e:
                logger.info(f"Error corrigiendo imports en {file_path}: {e}")
    
    def fix_logging_issues(self):
        """Corrige problemas de logging"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar si necesita configuración de logging
                if 'logging' in content and 'logger = logging.getLogger(__name__)' not in content:
                    # Buscar la línea después de import logging
                    lines = content.split('\n')
                    logging_import_line = -1
                    
                    for i, line in enumerate(lines):
                        if 'import logging' in line:
                            logging_import_line = i
                            break
                    
                    if logging_import_line != -1:
                        # Añadir configuración de logger
                        lines.insert(logging_import_line + 1, 'logger = logging.getLogger(__name__)')
                        
                        new_content = '\n'.join(lines)
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        self.fixes_applied.append(f"Configurado logging en {file_path}")
                
            except Exception as e:
                logger.info(f"Error corrigiendo logging en {file_path}: {e}")
    
    def fix_generic_exceptions(self):
        """Corrige excepciones genéricas"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Reemplazar except Exception: con except Exception:
                if 'except Exception:' in content:
                    new_content = content.replace('except Exception:', 'except Exception:')
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        self.fixes_applied.append(f"Corregidas excepciones genéricas en {file_path}")
                
            except Exception as e:
                logger.info(f"Error corrigiendo excepciones en {file_path}: {e}")
    
    def fix_print_statements(self):
        """Corrige print statements por logging"""
        python_files = list(self.project_root.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Reemplazar print() con logger.info()
                if 'logger.info(' in content:
                    # Asegurar que hay logger configurado
                    if 'logger = logging.getLogger(__name__)' not in content:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'import logging' in line:
                                lines.insert(i + 1, 'logger = logging.getLogger(__name__)')
                                break
                        content = '\n'.join(lines)
                    
                    # Reemplazar print statements
                    new_content = re.sub(r'print\s*\(([^)]+)\)', r'logger.info(\1)', content)
                    
                    if new_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        self.fixes_applied.append(f"Reemplazados print statements en {file_path}")
                
            except Exception as e:
                logger.info(f"Error corrigiendo print statements en {file_path}: {e}")
    
    def fix_requirements(self):
        """Corrige el archivo requirements.txt"""
        requirements_file = self.project_root / "requirements.txt"
        
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Añadir tkinter si no está presente
                if 'tkinter' not in content:
                    # tkinter viene con Python, pero lo añadimos como comentario
                    lines = content.split('\n')
                    lines.append('# tkinter comes with Python (no need to install)')
                    
                    new_content = '\n'.join(lines)
                    with open(requirements_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.fixes_applied.append("Añadido comentario sobre tkinter en requirements.txt")
                
            except Exception as e:
                logger.info(f"Error corrigiendo requirements.txt: {e}")
    
    def generate_fix_report(self) -> str:
        """Genera un reporte de las correcciones aplicadas"""
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE CORRECCIONES APLICADAS - SCRAPELILLO")
        report.append("=" * 60)
        report.append("")
        
        if self.fixes_applied:
            report.append("CORRECCIONES APLICADAS:")
            report.append("-" * 30)
            for fix in self.fixes_applied:
                report.append(f"✅ {fix}")
            report.append("")
        else:
            report.append("No se aplicaron correcciones.")
            report.append("")
        
        report.append("RECOMENDACIONES ADICIONALES:")
        report.append("-" * 30)
        report.append("1. Ejecutar tests después de aplicar correcciones")
        report.append("2. Verificar que las funcionalidades sigan funcionando")
        report.append("3. Revisar manualmente los archivos modificados")
        report.append("4. Ejecutar el verificador de errores nuevamente")
        
        return "\n".join(report)


def main():
    """Función principal"""
    logger.info("🔧 Corrector de Advertencias - Scrapelillo")
    logger.info("=" * 50)
    
    fixer = WarningFixer()
    
    # Aplicar correcciones
    fixes = fixer.fix_all_warnings()
    
    # Generar reporte
    report = fixer.generate_fix_report()
    logger.info("\n" + report)
    
    # Guardar reporte
    with open("fix_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"\n📄 Reporte de correcciones guardado en: fix_report.txt")
    
    if fixes:
        logger.info(f"✅ Se aplicaron {len(fixes)} correcciones")
    else:
        logger.info("ℹ️  No se aplicaron correcciones")


if __name__ == "__main__":
    main() 