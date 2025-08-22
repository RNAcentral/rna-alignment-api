from Bio import AlignIO
from io import StringIO
import re

def parse_stockholm_file(content):
    """
    Parse Stockholm format content and return complete MSA data structure.
    
    Args:
        content (str): Stockholm format content as string
    
    Returns:
        dict: Complete MSA data structure with sequences, consensus, and notation
    """
    # Debug: Check if content looks like Stockholm format
    if not content.strip():
        raise ValueError("Empty content provided")
    
    # Check for Stockholm header
    if "# STOCKHOLM" not in content:
        raise ValueError("Content does not appear to be Stockholm format (missing '# STOCKHOLM' header)")
    
    try:
        # Parse sequences using BioPython
        content_io = StringIO(content)
        alignment = AlignIO.read(content_io, "stockholm")
        
        sequences = []
        for record in alignment:
            sequences.append({
                'name': record.id,
                'sequence': str(record.seq)
            })
        
        # Parse additional annotations manually (BioPython doesn't handle all annotations well)
        reference_sequence = ""
        secondary_structure_consensus = ""
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract reference sequence (#=GC RF)
            if line.startswith('#=GC RF'):
                parts = line.split()
                if len(parts) >= 3:
                    reference_sequence += ''.join(parts[2:])
            
            # Extract secondary structure consensus (#=GC SS_cons)
            elif line.startswith('#=GC SS_cons'):
                parts = line.split()
                if len(parts) >= 3:
                    secondary_structure_consensus += ''.join(parts[2:])
        
        # Build result structure
        result = {
            'sequences': sequences,
            'consensus': reference_sequence if reference_sequence else None
        }
        
        # Parse secondary structure if available
        if secondary_structure_consensus:
            result['notation'] = parse_secondary_structure(secondary_structure_consensus)
        
        return result
    
    except Exception as e:
        # Debug info
        raise e

def parse_secondary_structure(consensus):
    """
    Parse secondary structure consensus string and base pairs.
    
    Args:
        consensus (str): Secondary structure consensus string (e.g., "<<<___>>>")
    
    Returns:
        dict: Secondary structure data with consensus and basePairs
    """
    base_pairs = []
    
   
    # Generate base pairs from < and > symbols
    base_pairs = generate_base_pair_links(consensus)
    
    return {
        'consensus': consensus,
        'basePairs': base_pairs
    }

def generate_base_pair_links(consensus):
    """
    Generate base pair links from < and > symbols in consensus string.
    
    Args:
        consensus (str): Secondary structure consensus string
    
    Returns:
        list: List of base pair dictionaries
    """
    base_pairs = []
    open_brackets = []  # Stack for tracking opening brackets
    
    for i, char in enumerate(consensus):
        position = i + 1  # Convert to 1-based position
        
        if char in '<([{':
            # Push position and type of opening bracket
            open_brackets.append((position, char))
        elif char in '>)]}':
            # Define matching pairs
            matches = {'>': '<', ')': '(', ']': '[', '}': '{'}
            
            # Match with most recent opening bracket of correct type
            if open_brackets:
                # Find the most recent matching opening bracket
                for j in range(len(open_brackets) - 1, -1, -1):
                    open_pos, open_char = open_brackets[j]
                    if open_char == matches[char]:
                        # Remove the matched opening bracket
                        open_brackets.pop(j)
                        base_pairs.append({
                            'x': open_pos,
                            'y': position,
                            'score': 1
                        })
                        break
    
    return base_pairs
