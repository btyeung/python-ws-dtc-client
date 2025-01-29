#!/usr/bin/env python
import argparse
import logging
import os
import sys
from dotenv import load_dotenv

from rest.rest_server_fastapi import RESTServer

if __name__ == '__main__':
    # Load environment variables from .env file
    load_dotenv()
    
    # Get DTC parameters from environment
    dtc_host = os.getenv('DTC_HOST', 'localhost')
    dtc_port = int(os.getenv('DTC_PORT', '11099'))
    dtc_history_port = int(os.getenv('DTC_HISTORY_PORT', '11098'))
    dtc_rest_port = int(os.getenv('DTC_REST_PORT', '8081'))
    
    parser = argparse.ArgumentParser(description='Start the FastAPI REST server')
    parser.add_argument('-p', '--port', type=int, help='REST server port (overrides DTC_REST_PORT)')
    parser.add_argument('--host', help='DTC host (overrides DTC_HOST)')
    parser.add_argument('--dtc-port', type=int, help='DTC port (overrides DTC_PORT)')
    parser.add_argument('--history-port', type=int, help='DTC history port (overrides DTC_HISTORY_PORT)')
    
    args = parser.parse_args()
    
    # Override environment variables with command line arguments if provided
    if args.port:
        dtc_rest_port = args.port
    if args.host:
        dtc_host = args.host
    if args.dtc_port:
        dtc_port = args.dtc_port
    if args.history_port:
        dtc_history_port = args.history_port
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logging.info(f"Starting FastAPI server with configuration:")
    logging.info(f"DTC Host: {dtc_host}")
    logging.info(f"DTC Port: {dtc_port}")
    logging.info(f"DTC History Port: {dtc_history_port}")
    logging.info(f"REST Port: {dtc_rest_port}")
    
    try:
        rest_server = RESTServer()
        rest_server.start(None, dtc_rest_port)  # dtc_client is set to None for standalone mode
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error starting server: {e}")
        sys.exit(1)