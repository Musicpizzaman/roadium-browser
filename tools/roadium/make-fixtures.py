#!/usr/bin/env python3
"""Create local media fixtures from a Chromium checkout."""
import argparse
import math
from pathlib import Path
import shutil
import struct
import wave


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    bear = args.source / 'media/test/data/bear.mp4'
    fixtures = Path(__file__).resolve().parent / 'fixtures'
    names = ('index.html', 'fullscreen-video.html')
    if not bear.is_file() or any(not (fixtures / name).is_file() for name in names):
        parser.error('Chromium bear.mp4 and repository HTML fixtures are required')
    if any((args.output / name).resolve() == original.resolve()
           for name, original in [('bear.mp4', bear)] +
           [(name, fixtures / name) for name in names]):
        parser.error('output must differ from the input asset directory')
    args.output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bear, args.output / 'bear.mp4')
    for name in names:
        shutil.copy2(fixtures / name, args.output / name)
    with wave.open(str(args.output / 'tone.wav'), 'wb') as wav:
        wav.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        wav.writeframes(b''.join(
            struct.pack('<h', int(2500 * math.sin(2 * math.pi * 440 * i / 16000)))
            for i in range(16000 * 5)))
    for name in (*names, 'bear.mp4', 'tone.wav'):
        path = args.output / name
        print(f'{name}: {path.stat().st_size} bytes')


if __name__ == '__main__':
    main()
