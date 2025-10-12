#!/usr/bin/env python3
"""
Diagnostic logging script to validate translation assumptions.
This should be added to the Docker container to track potential issues.
"""

import logging
import sys
import os
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/translation_debug.log'),
        logging.StreamHandler()
    ]
)

def log_translation_event(event_type, details):
    """Log translation-related events"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details
    }
    logging.info(f"TRANSLATION_EVENT: {log_entry}")

def log_source_mapping(source_names, mapped_ids, language):
    """Log source mapping attempts and results"""
    log_translation_event('SOURCE_MAPPING', {
        'input_names': source_names,
        'mapped_ids': mapped_ids,
        'language': language,
        'all_mapped_successfully': all(mapped_id is not None for mapped_id in mapped_ids)
    })

def log_language_switch(old_lang, new_lang):
    """Log language switch events"""
    log_translation_event('LANGUAGE_SWITCH', {
        'from_language': old_lang,
        'to_language': new_lang
    })

def log_data_retrieval_attempt(source_ids, keyword, success, error=None):
    """Log data retrieval attempts"""
    log_translation_event('DATA_RETRIEVAL', {
        'source_ids': source_ids,
        'keyword': keyword,
        'success': success,
        'error': str(error) if error else None
    })

def log_ui_rendering(component_name, language, source_names):
    """Log UI rendering events"""
    log_translation_event('UI_RENDERING', {
        'component': component_name,
        'language': language,
        'source_names': source_names
    })

# Example of how to integrate with app.py:
if __name__ == "__main__":
    print("This diagnostic logging module should be imported and used in app.py")
    print("Example usage:")
    print("from diagnostic_logging_for_translation import log_source_mapping")
    print("log_source_mapping(['Bain - Usability'], [3], 'en')")