#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
query_parser.py - Parse management tool queries and generate JSON files

This script reads a formatted text file containing management tool queries
and generates two JSON files:
1. single_term_queries.json - Contains single term search queries
2. boolean_logic_queries.json - Contains boolean logic for complex searches
"""

import json
import re
import os
from typing import Dict, List, Tuple

def parse_single_terms(optimized_query: str) -> List[str]:
    """
    Parse only the first part of optimized queries (before any +) to extract single search terms
    
    Args:
        optimized_query: String containing the optimized search pattern
        
    Returns:
        list: List of single terms to search
    """
    # Get only the first part (before any +)
    first_part = optimized_query.split('+')[0].strip()
    
    # If there's no complex pattern, just return the simple term
    if '"' in first_part and '|' not in first_part:
        # Remove quotes and return as single item
        return [first_part.replace('"', '').strip()]
    
    # Look for patterns like ("word1 | word2")
    pattern = r'\((.*?)\)'
    matches = re.findall(pattern, first_part)
    
    if not matches:
        # If no parentheses pattern found, return the simple term
        return [first_part.strip()]
    
    # Split the terms by | and clean them up
    terms = []
    for match in matches:
        parts = [part.strip().replace('"', '') for part in match.split('|')]
        terms.extend(parts)
    
    return terms

def parse_boolean_logic(optimized_query: str) -> str:
    """
    Parse the second part of optimized queries to create boolean logic
    
    Args:
        optimized_query: String containing the optimized search pattern
        
    Returns:
        str: Boolean logic expression or '#' if no second part exists
    """
    # Split by '+' if it exists (looking for the second part)
    parts = optimized_query.split('+', 1)
    
    if len(parts) == 1:
        return '#'  # No second part exists
    
    second_part = parts[1].strip()
    
    # Remove outer parentheses if they exist
    if second_part.startswith('(') and second_part.endswith(')'):
        second_part = second_part[1:-1].strip()
    
    # Parse the boolean logic
    # Replace " | " with " OR " for clarity
    # Handle the adjacent terms (word1 +word2) by joining them with AND_NEXT
    def process_term(term):
        term = term.strip().replace('"', '')
        if '+' in term:
            words = term.split('+')
            return ' AND_NEXT '.join(word.strip() for word in words)
        return term

    # Split by | and process each term
    if '|' in second_part:
        terms = second_part.split('|')
        processed_terms = [process_term(term) for term in terms]
        return ' OR '.join(processed_terms)
    else:
        return process_term(second_part)

def extract_tool_name(line: str) -> str:
    """
    Extract tool name from an Original line
    
    Args:
        line: Line containing the Original query
        
    Returns:
        str: Tool name
    """
    # Remove the number and 'Original:' prefix
    parts = line.split('Original:', 1)
    if len(parts) != 2:
        return None
    
    # Extract the tool name from the query
    query = parts[1].strip()
    # Remove quotes and get the first part before any '+'
    tool_name = query.replace('"', '').split('+')[0].strip()
    return tool_name

def parse_input_file(file_path: str) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """
    Parse the input file and extract queries
    
    Args:
        file_path: Path to the input file
        
    Returns:
        tuple: (single_term_mapping, boolean_logic_mapping)
    """
    single_term_mapping = {}
    boolean_logic_mapping = {}
    current_tool = None
    optimized_queries = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
                
            if 'Original:' in line:
                # If we have a previous tool, process it
                if current_tool and optimized_queries:
                    # Use the first query for single terms
                    single_term_mapping[current_tool] = parse_single_terms(optimized_queries[0])
                    # Use the last query for boolean logic
                    boolean_logic_mapping[current_tool] = parse_boolean_logic(optimized_queries[-1])
                
                # Start new tool
                current_tool = extract_tool_name(line)
                optimized_queries = []
                
            elif 'Optimizado:' in line:
                # Extract the optimized query
                query = line.split('Optimizado:', 1)[1].strip()
                optimized_queries.append(query)
                
            i += 1
        
        # Process the last tool
        if current_tool and optimized_queries:
            single_term_mapping[current_tool] = parse_single_terms(optimized_queries[0])
            boolean_logic_mapping[current_tool] = parse_boolean_logic(optimized_queries[-1])
    
    return single_term_mapping, boolean_logic_mapping

def main():
    """Main function to run the parser"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'input_queries.txt')
    
    print(f"Reading input file: {input_file}")
    
    # Parse the input file
    single_term_mapping, boolean_logic_mapping = parse_input_file(input_file)
    
    # Save to JSON files
    output_files = {
        'single_term_queries.json': single_term_mapping,
        'boolean_logic_queries.json': boolean_logic_mapping
    }
    
    for filename, data in output_files.items():
        output_path = os.path.join(script_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Generated: {output_path}")
    
    # Print example output
    print("\nSingle Term Queries:")
    print(json.dumps(single_term_mapping, indent=2))
    print("\nBoolean Logic Queries:")
    print(json.dumps(boolean_logic_mapping, indent=2))

if __name__ == "__main__":
    main() 