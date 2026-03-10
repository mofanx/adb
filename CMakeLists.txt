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
#

cmake_minimum_required(VERSION 3.14.2)
project(adb-build)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 20)
enable_language(ASM)

# set global cflags and cxxflags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fcolor-diagnostics -fPIC -Wno-attributes")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fcolor-diagnostics -fPIC -Wno-attributes")

# platform tools version
set(TOOLS_VERSION 35.0.2)
set(SRC ${PROJECT_SOURCE_DIR}/src)

# 64-bit off_t for lseek
add_definitions(-D_FILE_OFFSET_BITS=64)

set(PROTOC_COMPILER)

if(DEFINED PROTOC_PATH)
    set(PROTOC_COMPILER ${PROTOC_PATH})

    if(NOT EXISTS ${PROTOC_COMPILER})
        unset(PROTOC_PATH CACHE)
        message(FATAL_ERROR "Invalid protoc: ${PROTOC_COMPILER}, please check if the path is correct")
    endif()

    # check protoc version
    execute_process(
        COMMAND ${PROTOC_COMPILER} --version
        OUTPUT_VARIABLE PTOTOBUF_VERSION
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )

    if(NOT PTOTOBUF_VERSION MATCHES "^libprotoc*")
        unset(PROTOC_PATH CACHE)
        message(FATAL_ERROR "Invalid protoc: ${PROTOC_COMPILER}, this may not be an executable")
    endif()

    string(REGEX MATCH "([0-9]+)\\.([0-9]+)\\.([0-9]+)" VERSIONS ${PTOTOBUF_VERSION})
    if(VERSIONS VERSION_GREATER "3.21.12")
        message(WARNING "${PTOTOBUF_VERSION}, the protobuf version is too high, may be incompatible!!")
    endif()
endif()

# third-party libraries
add_subdirectory(src/boringssl EXCLUDE_FROM_ALL)
add_subdirectory(src/fmtlib EXCLUDE_FROM_ALL)
add_subdirectory(src/pcre EXCLUDE_FROM_ALL)
add_subdirectory(src/zstd/build/cmake EXCLUDE_FROM_ALL)
add_subdirectory(src/lz4/build/cmake EXCLUDE_FROM_ALL)
add_subdirectory(src/brotli EXCLUDE_FROM_ALL)
add_subdirectory(src/abseil-cpp EXCLUDE_FROM_ALL)
add_subdirectory(src/protobuf EXCLUDE_FROM_ALL)
add_subdirectory(src/googletest EXCLUDE_FROM_ALL)
add_subdirectory(src/jsoncpp EXCLUDE_FROM_ALL)

# building adb libraries and binary
add_subdirectory(lib)
add_subdirectory(platform-tools)
