#!/usr/bin/env python3
"""Script to remove emojis from all agent files"""
import os

# Emoji replacement map
EMOJI_MAP = {
    '🌙': '[OK]',
    '✨': '[OK]',
    '🎯': '[TARGET]',
    '💰': '[MONEY]',
    '📊': '[STATS]',
    '🏆': '[WINNER]',
    '💡': '[IDEA]',
    '🎉': '[PARTY]',
    '🚀': '[ROCKET]',
    '⚠️': '[WARNING]',
    '🔄': '[REFRESH]',
    '✅': '[OK]',
    '❌': '[ERROR]',
    '🤖': '[AI]',
    '🛡️': '[SHIELD]',
    '📈': '[UP]',
    '📉': '[DOWN]',
    '🧪': '[TEST]',
    '🚨': '[ALERT]',
    '🎭': '[MASK]',
    '📁': '[DIR]',
    '🔍': '[SEARCH]',
    '⚡': '[FAST]',
    '⭐': '[STAR]',
    '💎': '[DIAMOND]',
    '🔥': '[FIRE]',
    '💥': '[BOOM]',
    '🗑️': '[TRASH]',
    '📝': '[NOTE]',
    '🗣️': '[SPEECH]',
    '🌟': '[STAR2]',
    '⏰': '[CLOCK]',
    '🔐': '[LOCK]',
    '🎨': '[ART]',
    '⚙️': '[GEAR]',
    '📦': '[BOX]',
    '🛠️': '[TOOL]',
    '🎪': '[CIRCUS]',
    '🏅': '[MEDAL]',
    '💯': '[100]',
    '🌈': '[RAINBOW]',
    '🎵': '[MUSIC]',
    '📢': '[ANNOUNCE]',
    '💪': '[STRONG]',
    '🎊': '[CONFETTI]',
    '🌊': '[WAVE]',
    '🔮': '[CRYSTAL]',
    '🎲': '[DICE]',
    '🎁': '[GIFT]',
    '🎈': '[BALLOON]',
    '💫': '[SPARKLE]',
    '🌸': '[FLOWER]',
    '🌺': '[HIBISCUS]',
    '🌻': '[SUNFLOWER]',
    '🌹': '[ROSE]',
    '🌷': '[TULIP]',
    '🌼': '[Daisy]',
    '🍀': '[CLOVER]',
    '🍁': '[MAPLE]',
    '🍂': '[LEAF]',
    '🍃': '[LEAVES]',
    '🌱': '[SEEDLING]',
    '🌿': '[HERB]',
    '☘️': '[SHAMROCK]',
    '🎋': '[BAMBOO]',
    '🎍': '[PINE]',
    '🌲': '[TREE]',
    '🌳': '[TREE2]',
    '🌴': '[PALM]',
    '🌵': '[CACTUS]',
    '🌾': '[RICE]',
}

def fix_file(filepath):
    """Fix emojis in a single file"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original_content = content

    for emoji, replacement in EMOJI_MAP.items():
        content = content.replace(emoji, replacement)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def main():
    """Main function"""
    agents_dir = 'src/agents'

    fixed_count = 0
    for filename in os.listdir(agents_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(agents_dir, filename)
            if fix_file(filepath):
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == '__main__':
    main()
