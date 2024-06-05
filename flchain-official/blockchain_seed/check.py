def check_for_duplicate_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            line_counts = {}
            for line in file:
                stripped_line = line.strip()
                if stripped_line in line_counts:
                    line_counts[stripped_line] += 1
                else:
                    line_counts[stripped_line] = 1
        
        duplicates = {line: count for line, count in line_counts.items() if count > 1}
        
        if duplicates:
            print("Duplicate lines found:")
            for line, count in duplicates.items():
                print(f'"{line}" appears {count} times')
        else:
            print("No duplicate lines found.")
    
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
file_path = 'hash/node_model_cluster_hash.txt'
check_for_duplicate_lines(file_path)