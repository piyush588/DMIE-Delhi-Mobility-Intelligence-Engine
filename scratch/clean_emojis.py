import re
import os

def remove_emojis(text):
    # Regex for various emoji ranges
    emoji_pattern = re.compile(
        '['
        '\U0001f600-\U0001f64f'  # emoticons
        '\U0001f300-\U0001f5ff'  # symbols & pictographs
        '\U0001f680-\U0001f6ff'  # transport & map symbols
        '\U0001f1e0-\U0001f1ff'  # flags (iOS)
        '\U00002702-\U000027b0'
        '\U000024c2-\U0001f251'
        '\U0001f900-\U0001f9ff'  # supplemental symbols and pictographs
        '\U0001f000-\U0001f02b'  # playing cards
        '\U0001f004-\U0001f0cf'  # mahjong tiles/dominoes
        ']+', flags=re.UNICODE)
    # Also handle some common multi-byte emojis specifically if needed
    text = emoji_pattern.sub('', text)
    # Handle specific common emojis like the one used in the README
    text = re.sub(r'[\u2600-\u26ff\u2700-\u27bf]', '', text)
    return text

files = ['README.md', 'CONTRIBUTING.md']
for file_path in files:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = remove_emojis(content)
        
        # Clean up double spaces left behind in headers
        new_content = re.sub(r'#  ', '# ', new_content)
        new_content = re.sub(r'##  ', '## ', new_content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Cleaned {file_path}")
