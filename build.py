#!/usr/bin/env python3
#
# Copyright © 2024 mofanx
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import time
import shutil
import argparse
import subprocess
from pathlib import Path


def format_time(seconds):
    minute, sec = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    hour = int(hour)
    minute = int(minute)
    if minute < 1:
        sec = float('%.2f' % sec)
    else:
        sec = int(sec)
    if hour != 0:
        return '{}h{}m{}s'.format(hour, minute, sec)
    elif minute != 0:
        return '{}m{}s'.format(minute, sec)
    else:
        return '{}s'.format(sec)


def complete(args):
    """Strip debug symbols and organize output."""
    binary_dir = Path.cwd() / args.build / 'bin'
    strip = Path(args.ndk) / 'toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-strip'

    arch_map = {
        'arm64-v8a': 'aarch64',
        'armeabi-v7a': 'arm',
        'x86_64': 'x86_64',
        'x86': 'i686'
    }

    adb_binary = binary_dir / 'adb'
    if adb_binary.exists():
        # Strip debug symbols
        subprocess.run('{} -g {}'.format(strip, adb_binary), shell=True)
        # Rename with architecture suffix
        arch_name = arch_map.get(args.abi, args.abi)
        output_name = 'adb-{}'.format(arch_name)
        output_dir = Path.cwd() / 'output'
        output_dir.mkdir(exist_ok=True)
        shutil.copy2(adb_binary, output_dir / output_name)
        print('\033[1;32mOutput: {}\033[0m'.format(output_dir / output_name))
    else:
        print('\033[1;31mError: adb binary not found at {}\033[0m'.format(adb_binary))


def build(args):
    ndk = Path(args.ndk)
    cmake_toolchain_file = ndk / 'build/cmake/android.toolchain.cmake'
    if not cmake_toolchain_file.exists():
        raise ValueError('No such file: {}'.format(cmake_toolchain_file))

    command = [
        'cmake', '-GNinja',
        '-B {}'.format(args.build),
        '-DANDROID_NDK={}'.format(args.ndk),
        '-DCMAKE_TOOLCHAIN_FILE={}'.format(cmake_toolchain_file),
        '-DANDROID_PLATFORM=android-{}'.format(args.api),
        '-DCMAKE_ANDROID_ARCH_ABI={}'.format(args.abi),
        '-DANDROID_ABI={}'.format(args.abi),
        '-DCMAKE_SYSTEM_NAME=Android',
        '-Dprotobuf_BUILD_TESTS=OFF',
        '-DABSL_PROPAGATE_CXX_STD=ON',
        '-DANDROID_ARM_NEON=ON',
        '-DCMAKE_BUILD_TYPE=Release',
    ]

    if args.protoc is not None:
        if not Path(args.protoc).exists():
            raise ValueError('No such file: {}'.format(args.protoc))
        command.append('-DPROTOC_PATH={}'.format(args.protoc))

    result = subprocess.run(command)
    start_time = time.time()
    if result.returncode == 0:
        result = subprocess.run([
            'ninja', '-C', args.build, 'adb', '-j {}'.format(args.job)
        ])

    if result.returncode == 0:
        complete(args)
        end_time = time.time()
        print('\033[1;32mBuild success, cost time: {}\033[0m'.format(
            format_time(end_time - start_time)))
    else:
        print('\033[1;31mBuild failed!\033[0m')
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Build ADB for Android")
    tasks = os.cpu_count()

    parser.add_argument('--ndk', required=True, help='Set the NDK toolchain path')
    parser.add_argument('--abi', choices=['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'],
                        required=True, help='Build for the specified architecture')
    parser.add_argument('--api', default=30, help='Set android platform level (default: 30)')
    parser.add_argument('--build', default='build', help='The build directory')
    parser.add_argument('--job', default=tasks, help='Run N jobs in parallel (default: {})'.format(tasks))
    parser.add_argument('--protoc', help='Set the host protoc path')

    args = parser.parse_args()
    build(args)


if __name__ == '__main__':
    main()
