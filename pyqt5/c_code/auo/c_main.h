#ifndef C_MAIN_H
#define C_MAIN_H

__attribute__((visibility("default"))) int c_main_api(void);

// #ifdef BUILD_DLL
// #define DLL_SYMBOL __declspec(dllexport)
// #else
// #define DLL_SYMBOL __declspec(dllimport)
// #endif

// __declspec(dllexport) int c_main(void);
// __declspec(dllexport)是Microsoft specific extension (MSVC)，若是Linux的gcc compiler不支持
// 但mingw的gcc compiler是支持__declspec(dllexport)的
// 以通用性來說，用__declspec(dllexport)不是很好，所以可以用__attribute__((visibility("default")))來取代
// 可同時支援Linux和Windows

#endif /*C_MAIN_H*/