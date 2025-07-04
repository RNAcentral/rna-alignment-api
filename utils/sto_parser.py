from Bio import AlignIO
from io import StringIO

def parse_stockholm_file(content):
    """
    Parse Stockholm format content and return sequences as a list of dictionaries.
    
    Args:
        content (str): Stockholm format content as string
    
    Returns:
        list: List of dictionaries with 'name' and 'sequence' keys
    """
    # Debug: Check if content looks like Stockholm format
    if not content.strip():
        raise ValueError("Empty content provided")
    
    # Check for Stockholm header
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
        
        return sequences
    
    except Exception as e:
        # Debug info
        lines = content.split('\n')
        print(f"Content preview (first 5 lines):")
        for i, line in enumerate(lines[:5]):
            print(f"Line {i+1}: {repr(line)}")
        raise e

# Example usage:
if __name__ == "__main__":
    with open("your_file.sto", "r") as f:
        content = f.read()
    sequences = parse_stockholm_file(content)
    print(sequences[:4])  # Print first 4 sequences