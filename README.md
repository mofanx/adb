# ADB for Android

从 AOSP 源码构建适用于 Android 设备的 ADB 二进制文件，支持多种 CPU 架构，可直接集成到 Android 应用中。

## 支持的架构

| 文件名 | 架构 | Android ABI |
|--------|------|-------------|
| `adb-aarch64` | ARM 64-bit | arm64-v8a |
| `adb-arm` | ARM 32-bit | armeabi-v7a |
| `adb-x86_64` | x86 64-bit | x86_64 |
| `adb-i686` | x86 32-bit | x86 |

## 自动构建

本项目使用 GitHub Actions 自动构建。有两种触发方式：

1. **推送 tag**：推送 `v*` 格式的 tag 会自动触发构建并创建 Release
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **手动触发**：在 GitHub Actions 页面手动运行 workflow，可指定 AOSP 源码 tag

构建产物会自动上传到 GitHub Releases，包含所有架构的 ADB 二进制文件和 SHA-256 校验和。

## 手动构建

### 前提条件

- Linux x86_64 系统
- Python 3
- CMake >= 3.14
- Ninja
- Git
- Android NDK (推荐 r27c)

### 构建步骤

```bash
# 1. 克隆仓库
git clone https://github.com/mofanx/adb.git
cd adb

# 2. 下载 AOSP 源码
python3 get_source.py --tags platform-tools-35.0.2

# 3. 构建 host protobuf (用于生成 proto 文件)
cd src/protobuf && mkdir host-build && cd host-build
cmake -GNinja -Dprotobuf_BUILD_TESTS=OFF ..
ninja -j$(nproc) protoc
cd ../../..

# 4. 构建 ADB (以 arm64-v8a 为例)
python3 build.py \
    --ndk=/path/to/android-ndk-r27c \
    --abi=arm64-v8a \
    --build=build-aarch64 \
    --protoc=$(pwd)/src/protobuf/host-build/protoc

# 输出文件在 output/ 目录下
```

### 构建参数

```
--ndk       Android NDK 路径 (必填)
--abi       目标架构: arm64-v8a, armeabi-v7a, x86_64, x86 (必填)
--api       Android API level (默认: 30)
--build     构建目录 (默认: build)
--job       并行任务数 (默认: CPU核心数)
--protoc    Host protoc 路径 (用于生成 proto 文件)
```

## 集成到 Android 应用

### 方式一：通过 assets 目录

1. 将对应架构的 ADB 二进制文件放入 `app/src/main/assets/` 目录
2. 运行时复制到应用私有目录并设置可执行权限：

```kotlin
val adbFile = File(context.filesDir, "adb")
context.assets.open("adb-aarch64").use { input ->
    adbFile.outputStream().use { output ->
        input.copyTo(output)
    }
}
adbFile.setExecutable(true)
```

### 方式二：通过 jniLibs 目录

1. 将二进制文件重命名为 `libadb.so`
2. 放入对应架构目录：`app/src/main/jniLibs/arm64-v8a/libadb.so`
3. 运行时从 nativeLibraryDir 获取路径

## 致谢

- [AOSP](https://android.googlesource.com/) - Android 源码
- [lzhiyong/android-sdk-tools](https://github.com/lzhiyong/android-sdk-tools) - CMake 构建方案参考

## 许可证

ADB 源码遵循 [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)。
