# TODO list
## qml??
## c to python
* ctype, dll
* 
## python to c



# DLL檔`__declspec(dllexport)` vs `__attribute__((visibility("default")))`
## 1. `__declspec(dllexport)` 的特性
- **專屬於 Microsoft 平台**：
  - `__declspec(dllexport)` 是 **Microsoft 專有的擴展語法**，用於在 **Windows 平台**上導出動態鏈接庫（DLL）中的符號。
- **MinGW 支持**：
  - **MinGW 和 MinGW-w64** 工具鏈擴展了 GCC，使其能夠識別和使用 `__declspec(dllexport)`。
- **Linux 不支持**：
  - **Linux 的 GCC** 不支持 `__declspec(dllexport)`，因為這是 Windows 平台特有功能，不適合跨平台開發。

---

## 2. `__attribute__((visibility("default")))` 的優勢
- **通用性**：
  - `__attribute__((visibility("default")))` 是 GCC 提供的標準屬性，用於控制符號的可見性。
  - 適用於多平台，包括 Linux、Windows（通過 MinGW）和 macOS。
- **與 ELF 格式兼容**：
  - 在 Linux 等基於 ELF 格式的系統中，這種屬性更標準化，推薦使用。
## 3. 為什麼 __declspec(dllexport) 不具通用性？
- __declspec(dllexport) 是針對 PE（Portable Executable）格式的 Windows 特定設計，對其他平台如 ELF 或 Mach-O 格式並不適用。
- 如果使用 __declspec(dllexport)，代碼將無法在非 Windows 平台（如 Linux 和 macOS）上編譯。
## 4. 通用性推薦
- 如果你需要代碼在多個平台上編譯並運行，建議使用 __attribute__((visibility("default")))，因為它適用於所有支持 ELF 的平台和 Windows（通過 GCC）。
- 如果僅在 Windows 上使用，__declspec(dllexport) 是可以接受的選擇，但考慮到可移植性，還是建議使用 __attribute__((visibility("default")))。
## 5. 小結
- __declspec(dllexport)：僅適用於 Windows（MSVC 和 MinGW 支持）。
- __attribute__((visibility("default")))：通用，支持 Linux、Windows 和 macOS。
- 最佳實踐：如果需要跨平台代碼，應該選擇 __attribute__((visibility("default")))，避免對特定編譯器或平台的依賴。
