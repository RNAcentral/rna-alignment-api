from Bio import AlignIO
from io import StringIO
import re

def parse_stockholm_file(content):
    """
    Parse Stockholm format content and return complete MSA data structure.
    
    Args:
        content (str): Stockholm format content as string
    
    Returns:
        dict: Complete MSA data structure with sequences, reference, and secondary structure
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
            'reference': reference_sequence if reference_sequence else None
        }
        
        # Parse secondary structure if available
        if secondary_structure_consensus:
            result['secondaryStructure'] = parse_secondary_structure(secondary_structure_consensus)
        
        return result
    
    except Exception as e:
        # Debug info
        lines = content.split('\n')
        print(f"Content preview (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            print(f"Line {i+1}: {repr(line)}")
        raise e

def parse_secondary_structure(consensus):
    """
    Parse secondary structure consensus string and return features and base pairs.
    
    Args:
        consensus (str): Secondary structure consensus string (e.g., "<<<___>>>")
    
    Returns:
        dict: Secondary structure data with consensus, features, and basePairs
    """
    features = []
    base_pairs = []
    
    # Parse features (stems and loops)
    current_feature = None
    
    for i, char in enumerate(consensus):
        position = i + 1  # 1-based position
        
        # Determine feature type
        if char in '<>':
            feature_type = 'stem'
        elif char == '_':
            feature_type = 'loop'
        elif char == ':':
            feature_type = 'single_strand'
        else:
            feature_type = 'single_strand'
        
        # Check if we need to start a new feature
        if not current_feature or current_feature['type'] != feature_type:
            # End the current feature if it exists
            if current_feature:
                features.append({
                    'start': current_feature['start'],
                    'end': position - 1,
                    'type': current_feature['type'],
                    'description': get_feature_description(current_feature['type'])
                })
            
            # Start a new feature
            current_feature = {
                'start': position,
                'type': feature_type
            }
    
    # Close any remaining feature
    if current_feature:
        features.append({
            'start': current_feature['start'],
            'end': len(consensus),
            'type': current_feature['type'],
            'description': get_feature_description(current_feature['type'])
        })
    
    # Filter to only include stem and loop features (length >= 2)
    filtered_features = [
        feature for feature in features 
        if feature['type'] in ['stem', 'loop'] and feature['end'] - feature['start'] >= 1
    ]
    
    # Generate base pairs from < and > symbols
    base_pairs = generate_base_pair_links(consensus)
    
    return {
        'consensus': consensus,
        'features': filtered_features,
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
        
        if char == '<':
            # Push position of opening bracket
            open_brackets.append(position)
        elif char == '>':
            # Match with most recent opening bracket
            if open_brackets:
                open_pos = open_brackets.pop()
                base_pairs.append({
                    'x': open_pos,
                    'y': position,
                    'a': 0,
                    'b': 8,
                    'score': 0.99
                })
    
    return base_pairs

def get_feature_description(feature_type):
    """
    Get human-readable description for feature type.
    
    Args:
        feature_type (str): Feature type ('stem', 'loop', etc.)
    
    Returns:
        str: Human-readable description
    """
    descriptions = {
        'stem': 'STEM',
        'loop': 'LOOP',
        'single_strand': 'Single Strand'
    }
    return descriptions.get(feature_type, 'RNA structural element')

# Example usage:
if __name__ == "__main__":
    with open("your_file.sto", "r") as f:
        content = f.read()
    
    msa_data = parse_stockholm_file(content)
    
    print("Sequences:", len(msa_data['sequences']))
    print("Reference:", bool(msa_data.get('reference')))
    print("Secondary Structure:", bool(msa_data.get('secondaryStructure')))
    
    if msa_data.get('secondaryStructure'):
        ss = msa_data['secondaryStructure']
        print("  Consensus length:", len(ss['consensus']))
        print("  Features:", len(ss['features']))
        print("  Base pairs:", len(ss['basePairs']))