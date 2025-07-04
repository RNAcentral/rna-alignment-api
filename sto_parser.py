
from Bio import AlignIO

def parse_stockholm_file(file_path):
    """
    Parse a Stockholm format file and return sequences as a list of dictionaries.
    
    Args:
        file_path (str): Path to the Stockholm format file (.sto)
    
    Returns:
        list: List of dictionaries with 'name' and 'sequence' keys
    """
    alignment = AlignIO.read(file_path, "stockholm")
    
    sequences = []
    for record in alignment:
        sequences.append({
            'name': record.id,
            'sequence': str(record.seq)
        })
    
    return sequences

# Example usage:
if __name__ == "__main__":
    sequences = parse_stockholm_file("your_file.sto")
    print(sequences[:4])  # Print first 4 sequences