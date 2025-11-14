"""
Smart Hiring System - Main Entry Point for Packaged Application
This file serves as the entry point for PyInstaller executable
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = Path(sys.executable).parent
    sys.path.insert(0, str(application_path))
else:
    # Running as script
    application_path = Path(__file__).parent.parent
    sys.path.insert(0, str(application_path))

# Import after path setup
from backend.backend_config import config
from backend.app import app
import logging


def main():
    """Main entry point for the application"""
    
    # Setup logging
    logger = config.setup_logging()
    
    logger.info("="*60)
    logger.info("🚀 Starting Smart Hiring System")
    logger.info("="*60)
    
    # Log configuration summary
    config_summary = config.get_config_summary()
    for key, value in config_summary.items():
        logger.info(f"   {key}: {value}")
    
    logger.info("="*60)
    
    # Validate configuration
    is_valid, errors = config.validate()
    if not is_valid:
        logger.warning("⚠️  Configuration validation issues:")
        for error in errors:
            logger.warning(f"   - {error}")
    
    try:
        # Start Flask application
        logger.info(f"🔗 Starting API server on port {config.PORT}")
        logger.info(f"🌐 Access at: http://localhost:{config.PORT}")
        logger.info(f"📊 Health check: http://localhost:{config.PORT}/api/health")
        logger.info("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=config.PORT,
            debug=config.DEBUG,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
