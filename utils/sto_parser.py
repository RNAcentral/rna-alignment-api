from Bio import AlignIO
from io import StringIO
import re

def parse_stockholm_file(content):
    if not content.strip():
        raise ValueError("Empty content provided")
    
    if "# STOCKHOLM" not in content:
        raise ValueError("Content does not appear to be Stockholm format (missing '# STOCKHOLM' header)")
    
    try:
        content_io = StringIO(content)
        alignment = AlignIO.read(content_io, "stockholm")
        
        sequences = []
        for record in alignment:
            sequences.append({
                'name': record.id,
                'sequence': str(record.seq)
            })
        
        reference_sequence = ""
        secondary_structure_consensus = ""
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('#=GC RF'):
                parts = line.split()
                if len(parts) >= 3:
                    reference_sequence += ''.join(parts[2:])
            
            elif line.startswith('#=GC SS_cons '):
                parts = line.split()
                if len(parts) >= 3:
                    secondary_structure_consensus += ''.join(parts[2:])
        
        result = {
            'sequences': sequences,
            'consensus': reference_sequence if reference_sequence else None
        }
        
        if secondary_structure_consensus:
            result['notation'] = parse_secondary_structure(secondary_structure_consensus)
        
        return result
    
    except Exception as e:
        raise e

def parse_secondary_structure(consensus):
    base_pairs = []
    
    base_pairs = generate_base_pair_links(consensus)
    
    return {
        'consensus': consensus,
        'basePairs': base_pairs
    }

def generate_base_pair_links(consensus):
    base_pairs = []
    open_brackets = []
    
    for i, char in enumerate(consensus):
        position = i + 1
        
        if char in '<([{':
            open_brackets.append((position, char))
        elif char in '>)]}':
            matches = {'>': '<', ')': '(', ']': '[', '}': '{'}
            
            if open_brackets:
                for j in range(len(open_brackets) - 1, -1, -1):
                    open_pos, open_char = open_brackets[j]
                    if open_char == matches[char]:
                        open_brackets.pop(j)
                        base_pairs.append({
                            'x': open_pos,
                            'y': position,
                            'score': 1
                        })
                        break
    
    return base_pairs