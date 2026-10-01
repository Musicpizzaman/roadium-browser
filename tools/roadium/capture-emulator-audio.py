#!/usr/bin/env python3
"""Measure AAOS emulator speaker PCM; requires grpcio in a local Python environment."""
import argparse
import array
import configparser
import json
import math
from pathlib import Path
import sys

REQUEST = bytes.fromhex('08 80 f7 02 10 01 18 01')


def read_endpoint(path, serial):
    try:
        cfg = configparser.ConfigParser(interpolation=None)
        cfg.read_string('[emulator]\n' + Path(path).read_text(encoding='utf-8'))
        values = cfg['emulator']
        if int(values['port.serial']) != serial:
            raise ValueError()
        port = int(values['grpc.port'])
        token = values['grpc.token'].strip()
        if not 1 <= port <= 65535 or not token or '\r' in token or '\n' in token:
            raise ValueError()
        return port, token
    except (OSError, UnicodeError, configparser.Error, KeyError, ValueError):
        raise ValueError('Invalid or mismatched emulator discovery file') from None


def read_varint(data, offset):
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(data):
            raise ValueError('Truncated protobuf varint')
        byte = data[offset]
        offset += 1
        if shift == 63 and byte > 1:
            raise ValueError('Protobuf varint exceeds uint64')
        value |= (byte & 127) << shift
        if byte < 128:
            return value, offset
    raise ValueError('Overlong protobuf varint')


def parse_fields(data):
    fields = {}
    offset = 0
    while offset < len(data):
        tag, offset = read_varint(data, offset)
        number, wire = tag >> 3, tag & 7
        if not 1 <= number < (1 << 29):
            raise ValueError('Invalid protobuf field number')
        if wire == 0:
            value, offset = read_varint(data, offset)
        elif wire in (1, 2, 5):
            if wire == 2:
                length, offset = read_varint(data, offset)
            else:
                length = 8 if wire == 1 else 4
            end = offset + length
            if end > len(data):
                raise ValueError('Truncated protobuf field')
            value = data[offset:end]
            offset = end
        else:
            raise ValueError('Unsupported protobuf wire type')
        fields[number] = (wire, value)
    return fields


def parse_audio_packet(data):
    fields = parse_fields(data)
    if 1 in fields:
        if fields[1][0] != 2:
            raise ValueError('Invalid audio format wire type')
        fmt = parse_fields(fields[1][1])
        expected = {1: 48000, 2: 1, 3: 1}
        if any(fmt.get(key) != (0, value) for key, value in expected.items()):
            raise ValueError('Unexpected audio format')
    timestamp = fields.get(2)
    audio = fields.get(3, (2, b''))
    if timestamp is None or timestamp[0] != 0 or audio[0] != 2:
        raise ValueError('Missing or invalid audio fields')
    if len(audio[1]) % 4:
        raise ValueError('Partial S16 stereo frame')
    return timestamp[1], audio[1]


def pcm_metrics(pcm):
    values = array.array('h')
    values.frombytes(pcm)
    if sys.byteorder != 'little':
        values.byteswap()
    count = len(values)
    energy = sum(int(value) ** 2 for value in values)
    peak = max((abs(int(value)) for value in values), default=0)
    return count, energy, peak


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--discovery', required=True, type=Path)
    parser.add_argument('--serial', type=int, default=5554)
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if not math.isfinite(args.seconds) or not 0 < args.seconds <= 600:
        parser.error('--seconds must be between 0 and 600')
    if args.output.resolve() == args.discovery.resolve():
        parser.error('output must differ from discovery file')
    try:
        import grpc
    except ImportError:
        print('Install grpcio in a local Python environment to use this tool.', file=sys.stderr)
        return 2
    try:
        port, token = read_endpoint(args.discovery, args.serial)
        samples = energy = peak = packets = 0
        # The installed emulator exposes its authenticated service on IPv4 loopback.
        with grpc.insecure_channel(f'127.0.0.1:{port}') as channel:
            stream = channel.unary_stream(
                '/android.emulation.control.EmulatorController/streamAudio',
                request_serializer=lambda value: value,
                response_deserializer=lambda value: value,
            )
            responses = stream(
                REQUEST, timeout=args.seconds,
                metadata=(('authorization', f'Bearer {token}'),),
            )
            with args.output.open('w', encoding='utf-8', newline='\n') as output:
                try:
                    for data in responses:
                        timestamp, pcm = parse_audio_packet(data)
                        count, packet_energy, packet_peak = pcm_metrics(pcm)
                        if not count:
                            continue
                        row = {
                            'timestamp_us': timestamp,
                            'bytes': len(pcm),
                            'sample_count': count,
                            'rms': math.sqrt(packet_energy / count),
                            'peak': packet_peak,
                        }
                        output.write(json.dumps(row) + '\n')
                        output.flush()
                        samples += count
                        energy += packet_energy
                        peak = max(peak, packet_peak)
                        packets += 1
                except grpc.RpcError as error:
                    if error.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
                        print(f'Audio capture failed: {error.code().name}', file=sys.stderr)
                        return 1
        summary = {
            'packets': packets, 'sample_count': samples, 'peak': peak,
            'rms': math.sqrt(energy / samples) if samples else 0,
            'seconds_requested': args.seconds,
        }
        print(json.dumps(summary))
        if not samples:
            print('No PCM received; this is not evidence of silence.', file=sys.stderr)
            return 1
        return 0
    except (OSError, ValueError):
        print('Invalid capture data, discovery file or output path.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
