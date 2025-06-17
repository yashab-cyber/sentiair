#!/usr/bin/env python3
"""
Sentinair - Offline AI-Powered Behavioral Threat Detection System
Main entry point for the application
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.engine import SentinairEngine
from gui.main_window import SentinairGUI
from cli.cli_interface import SentinairCLI
from utils.config import Config
from utils.logger import setup_logging

def main():
    """Main entry point for Sentinair application"""
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Sentinair - Offline AI-Powered Behavioral Threat Detection System"
    )
    parser.add_argument(
        "--mode", 
        choices=["gui", "cli", "stealth"], 
        default="gui",
        help="Application mode (default: gui)"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/default.yaml",
        help="Configuration file path"
    )
    parser.add_argument(
        "--log-level", 
        choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--stealth-key", 
        type=str,
        help="Stealth mode unlock key"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config = Config(args.config)
        
        # Initialize core engine
        engine = SentinairEngine(config)
        
        # Start application based on mode
        if args.mode == "gui":
            logger.info("Starting Sentinair in GUI mode")
            app = SentinairGUI(engine, config)
            app.run()
            
        elif args.mode == "cli":
            logger.info("Starting Sentinair in CLI mode")
            cli = SentinairCLI(engine, config)
            cli.run()
            
        elif args.mode == "stealth":
            logger.info("Starting Sentinair in stealth mode")
            if not args.stealth_key:
                logger.error("Stealth mode requires --stealth-key parameter")
                sys.exit(1)
            
            # Validate stealth key
            if not config.validate_stealth_key(args.stealth_key):
                logger.error("Invalid stealth key")
                sys.exit(1)
                
            # Run in stealth mode (background)
            engine.run_stealth_mode()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
