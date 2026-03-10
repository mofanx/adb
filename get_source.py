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
import shutil
import argparse
import subprocess
import json
import urllib.request
from pathlib import Path


DEPLOYAGENT_INC_URL = "https://raw.githubusercontent.com/lzhiyong/android-sdk-tools/master/patches/misc/deployagent.inc"


def download_deployagent():
    """Download deployagent.inc from reference project (large binary file)."""
    dest = Path("patches/misc/deployagent.inc")
    if dest.exists():
        return
    print("Downloading deployagent.inc ...")
    urllib.request.urlretrieve(DEPLOYAGENT_INC_URL, str(dest))
    print("Downloaded deployagent.inc")


def patches():
    """Apply necessary patches to make AOSP source buildable with NDK."""
    # Create incremental delivery sysprop include directory
    inc = Path.cwd() / "src/incremental_delivery/sysprop/include"
    if not inc.exists():
        inc.mkdir(parents=True)
    shutil.copy2(Path("patches/misc/IncrementalProperties.sysprop.h"), inc)
    shutil.copy2(Path("patches/misc/IncrementalProperties.sysprop.cpp"), inc.parent)

    # Copy deploy agent inc files
    deploy_dir = Path("src/adb/fastdeploy/deployagent")
    if deploy_dir.exists():
        shutil.copy2(Path("patches/misc/deployagent.inc"), deploy_dir)
        shutil.copy2(Path("patches/misc/deployagentscript.inc"), deploy_dir)

    # Copy platform tools version header
    version_dir = Path("src/soong/cc/libbuildversion/include")
    if version_dir.exists():
        shutil.copy2(Path("patches/misc/platform_tools_version.h"), version_dir)

    # Fix abseil-cpp googletest path
    abseil_cmake = Path.cwd() / "src/abseil-cpp/CMakeLists.txt"
    if abseil_cmake.exists():
        pattern = "'s#/usr/src/googletest#${CMAKE_SOURCE_DIR}/src/googletest#g'"
        subprocess.run("sed -i {} {}".format(pattern, abseil_cmake), shell=True)

    # Fix protobuf missing config.h for CMake builds
    protobuf_stubs = Path.cwd() / "src/protobuf/src/google/protobuf/stubs"
    config_dest = protobuf_stubs / "config.h"
    if protobuf_stubs.exists() and not config_dest.exists():
        shutil.copy2(Path("patches/misc/protobuf_config.h"), config_dest)

    # Fix openscreen packaged_task noexcept incompatibility with NDK libc++
    task_runner_h = Path.cwd() / "src/openscreen/platform/api/task_runner.h"
    if task_runner_h.exists():
        subprocess.run(
            "sed -i 's/packaged_task<void() noexcept>/packaged_task<void()>/g' {}".format(task_runner_h),
            shell=True)

    # Symlink googletest to boringssl third_party
    src = Path.cwd() / "src/googletest"
    dest = Path.cwd() / "src/boringssl/src/third_party/googletest"
    if src.exists() and not dest.exists():
        subprocess.run("ln -sf {} {}".format(src, dest), shell=True)


def main():
    parser = argparse.ArgumentParser(description="Fetch AOSP source code for ADB build")
    parser.add_argument("--tags", default="platform-tools-35.0.2",
                        help="Specify the Git cloning tags or branch (default: platform-tools-35.0.2)")
    args = parser.parse_args()

    # Git clone submodules
    with open('repos.json', 'r') as file:
        repos = json.load(file)
    for repo in repos:
        if not Path(repo['path']).exists():
            print("Cloning {} -> {}".format(repo['url'], repo['path']))
            subprocess.run(
                'git clone -c advice.detachedHead=false --depth 1 --branch {} {} {}'.format(
                    args.tags, repo['url'], repo['path']),
                shell=True
            )

    # Download large binary patch files
    download_deployagent()

    # Apply patches
    patches()

    print("Source code download complete!")


if __name__ == "__main__":
    main()
