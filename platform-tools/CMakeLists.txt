#
# Platform tools - ADB only
#

project(platform-tools)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)

include(adb.cmake)
