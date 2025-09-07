# 🌐 Tron Browser

<div align="center">

![Tron Browser](https://img.shields.io/badge/Version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5%2B-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Un navegador web moderno y potente construido con Python y PySide6**

🔍 **Scraping Avanzado** • 🤖 **Chat IA Integrado** • 🌐 **Gestión de Proxies** • 🔒 **Privacidad**

[Características](#-características-principales) • [Instalación](#-instalación) • [Uso](#-uso) • [Contribuir](#-contribuir)

</div>

## ✨ Características Principales

### 🌐 Navegación Web
- **Múltiples pestañas**: Navegación fluida con gestión avanzada de pestañas
- **Marcadores inteligentes**: Sistema de marcadores con categorías
- **Historial de navegación**: Búsqueda y gestión completa del historial
- **Gestor de contraseñas**: Almacenamiento seguro de credenciales
- **Configuración de privacidad**: Control granular sobre cookies y datos

### 🔍 Herramientas de Scraping
- **Análisis de HTML**: Extracción inteligente de datos de páginas web
- **Selección interactiva**: Clic en elementos para extraer información
- **Exportación múltiple**: CSV, Excel, JSON, YAML
- **Descubrimiento de URLs**: Encuentra enlaces automáticamente

### 🌐 Gestión de Proxies
- **Rotación automática**: Cambio inteligente entre proxies
- **Configuración avanzada**: HTTP, HTTPS, SOCKS
- **Monitoreo de estado**: Verificación de conectividad en tiempo real
- **Importación masiva**: Carga de listas de proxies

### 🤖 **Chat con IA (NUEVO)**
- **Integración con LM Studio**: Chat con modelos de lenguaje local
- **Contexto de página**: La IA conoce la página que estás visitando
- **Historial de conversaciones**: Guardado automático de chats
- **Configuración avanzada**: Temperatura, tokens, personalización
- **Exportación de chats**: Guarda conversaciones importantes

## 🚀 Instalación

### Requisitos Previos
- Python 3.8+
- LM Studio (opcional, para el chat con IA)

### Instalación Rápida

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu-usuario/tron-browser.git
cd tron-browser
```

2. **Crear entorno virtual** (recomendado):
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar (opcional)**:
```bash
# Copiar archivos de configuración de ejemplo
cp scrapelillo/config/config.example.yaml scrapelillo/config/config.yaml
cp scrapelillo/config/proxies.example.txt scrapelillo/config/proxies.txt
```

5. **Ejecutar el navegador**:
```bash
python main.py
```

## 🖼️ Capturas de Pantalla

*Próximamente: Capturas de pantalla de la interfaz*

## 🎯 Uso

### Navegación Básica
- **Nueva pestaña**: Ctrl+T
- **Cerrar pestaña**: Ctrl+W
- **Recargar**: F5 o Ctrl+R
- **Historial**: Ctrl+H
- **Marcadores**: Ctrl+B

### Funciones Avanzadas
- **Panel de Scraping**: Haz clic en el icono 🔍 en la barra lateral
- **Gestión de Proxies**: Haz clic en el icono 🌐 en la barra lateral
- **Chat IA**: Haz clic en el icono 🤖 en la barra lateral
- **Configuración de Privacidad**: Haz clic en el icono 🔒 en la barra lateral

## 🤖 Configuración del Chat con IA

### 1. Instalar LM Studio
- Descarga desde [https://lmstudio.ai/](https://lmstudio.ai/)
- Instala y descarga un modelo de IA (Llama 2, Mistral, etc.)

### 2. Iniciar Servidor Local
- Abre LM Studio
- Ve a "Local Server"
- Haz clic en "Start Server"
- Anota la URL (típicamente `http://localhost:1234`)

### 3. Configurar en Tron Browser
- Abre Tron Browser
- Haz clic en "🤖 Chat IA" en la barra de navegación
- Ve a "⚙️ Configuración"
- Ingresa la URL del servidor
- Prueba la conexión

## 📋 Uso del Chat con IA

### Enviar Mensajes
1. Escribe tu mensaje en el área de texto
2. Opcionalmente, marca "Incluir contexto de página actual"
3. Haz clic en "📤 Enviar"
4. ¡Disfruta de la respuesta de la IA!

### Características Avanzadas
- **Contexto inteligente**: La IA conoce la página que visitas
- **Historial persistente**: Conversaciones guardadas automáticamente
- **Exportación**: Guarda chats importantes en JSON
- **Configuración**: Ajusta creatividad y longitud de respuestas

## 🛠️ Funcionalidades Avanzadas

### Scraping Inteligente
```python
# El panel de scraping permite:
- Análisis automático de HTML
- Selección visual de elementos
- Extracción de datos estructurados
- Exportación en múltiples formatos
```

### Gestión de Proxies
```python
# Sistema completo de proxies:
- Rotación automática
- Verificación de conectividad
- Configuración por tipo (HTTP/HTTPS/SOCKS)
- Importación desde archivos
```

### Chat con IA
```python
# Conversaciones inteligentes:
- Integración con LM Studio
- Contexto de página actual
- Historial de conversaciones
- Configuración personalizable
```

## 🔧 Configuración

### Temas
- **Tema claro**: Interfaz limpia y moderna
- **Tema oscuro**: Protección visual y ahorro de batería
- **Cambio dinámico**: Alterna entre temas con un clic

### Privacidad
- **Control de cookies**: Gestión granular
- **Datos de navegación**: Limpieza automática
- **Configuración por sitio**: Personalización avanzada

## 🎯 Casos de Uso

### Investigación Web
1. **Navega** a páginas de interés
2. **Usa el chat** para analizar contenido
3. **Extrae datos** con herramientas de scraping
4. **Exporta resultados** en tu formato preferido

### Automatización
1. **Configura proxies** para rotación
2. **Usa scraping** para recopilar datos
3. **Procesa información** con el chat IA
4. **Exporta resultados** automáticamente

### Desarrollo Web
1. **Inspecciona elementos** con DevTools
2. **Analiza estructura** con scraping
3. **Consulta la IA** sobre código y diseño
4. **Documenta hallazgos** en el chat


---

<div align="center">

**⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub! ⭐**

¡Disfruta navegando con **Tron Browser**! 🚀

</div> 
