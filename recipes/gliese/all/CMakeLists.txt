cmake_minimum_required(VERSION 3.16)

option(BUILD_STATIC_GLIESE "Build static library Gliese" OFF)
option(BUILD_RUNTIME_STATIC "Build static runtime" OFF)

if (BUILD_STATIC_GLIESE OR NOT BUILD_SHARED_LIBS)
  set(Boost_USE_STATIC_LIBS ON)
  set(Boost_ALL_DYN_LINK OFF)
  set(BUILD_STATIC_LIBS ON)
  set(BUILD_SHARED_LIBS OFF)
  set(BUILD_STATIC_LIBS ON)
else()
  set(BUILD_STATIC_LIBS OFF)
  set(Boost_USE_STATIC_LIBS OFF)
  set(Boost_ALL_DYN_LINK ON)
  set(BUILD_SHARED_LIBS ON)
  set(BUILD_STATIC_LIBS OFF)
  set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()
if(BUILD_STATIC_RUNTIME)
if (MSVC)
    add_compile_options(
      $<$<CONFIG:>:/MT> #---------|
      $<$<CONFIG:Debug>:/MTd> #---|-- Statically link the runtime libraries
      $<$<CONFIG:Release>:/MT> #--|
    )
    set(CMAKE_FIND_LIBRARY_SUFFIXES ".lib")
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    if (WIN32)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a .lib")
    elseif(UNIX OR APPLE)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
    endif()
    set(CMAKE_EXE_LINKER_FLAGS "-static -static-libgcc -static-libstdc++")
  elseif("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    if (WIN32)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a .lib")
    elseif(UNIX OR APPLE)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
    endif()
    set(CMAKE_EXE_LINKER_FLAGS "-static")
  endif()
  set(Boost_RUNTIME_LINK "static")
  set(Boost_USE_STATIC_RUNTIME ON)
else()
if (MSVC)
    add_compile_options(
      $<$<CONFIG:>:/MD> #---------|
      $<$<CONFIG:Debug>:/MDd> #---|-- Dynamically link the runtime libraries
      $<$<CONFIG:Release>:/MD> #--|
    )
    set(CMAKE_FIND_LIBRARY_SUFFIXES ".dll")
  elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    if (WIN32)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".a .lib")
    elseif(UNIX)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".so")
    elseif(APPLE)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".dylib")
    endif()
    set(CMAKE_EXE_LINKER_FLAGS "-shared")
  elseif("${CMAKE_CXX_COMPILER_ID}" MATCHES "Clang")
    if (WIN32)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".dll")
    elseif(UNIX)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".so")
    elseif(APPLE)
      set(CMAKE_FIND_LIBRARY_SUFFIXES ".dylib")
    endif()
    set(CMAKE_EXE_LINKER_FLAGS "-shared -undefined dynamic_lookup")
  endif()
  set(Boost_RUNTIME_LINK "shared")
  set(Boost_USE_STATIC_RUNTIME OFF)
endif()
project(Gliese)

set(BUILD_SHARED_LIBS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include conan paths to locate dependencies
list(APPEND CMAKE_PREFIX_PATH "${CMAKE_BINARY_DIR}")

# If conan.cmake does not exist, download it
if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
    message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
    file(DOWNLOAD "https://raw.githubusercontent.com/conan-io/cmake-conan/master/conan.cmake"
        "${CMAKE_BINARY_DIR}/conan.cmake")
endif()

# Include the downloaded conan.cmake
include(${CMAKE_BINARY_DIR}/conan.cmake)

# Install dependencies via Conan
conan_cmake_install(PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR}
    BUILD missing
    GENERATORS cmake_find_package)

# Include directories for the project
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Specify source files
set(SOURCE_FILES
    src/Gliese/HttpClient/HttpClient.cpp
    src/Gliese/HttpsClient/HttpsClient.cpp
    src/Gliese/WebClient/WebClient.cpp
)

# Find required packages
find_package(jsoncpp REQUIRED)
if(jsoncpp_FOUND)
    include_directories(${jsoncpp_INCLUDE_DIRS})
    list(APPEND LIBRARIES ${jsoncpp_LIBRARIES})
endif()
find_package(fmt REQUIRED)
if(fmt_FOUND)
    include_directories(${fmt_INCLUDE_DIRS})
    list(APPEND LIBRARIES ${fmt_LIBRARIES})
endif()
find_package(cppcoro REQUIRED)
if(cppcoro_FOUND)
    include_directories(${cppcoro_INCLUDE_DIRS})
    list(APPEND LIBRARIES ${cppcoro_LIBRARIES})
endif()
find_package(OpenSSL REQUIRED)
if(OpenSSL_FOUND)
    include_directories(${OpenSSL_INCLUDE_DIRS})
    list(APPEND LIBRARIES ${OpenSSL_LIBRARIES})
endif()
# If the packages are found, add them to the list of libraries
# list(APPEND LIBRARIES jsoncpp fmt cppcoro OpenSSL::SSL OpenSSL::Crypto)

# Fetch Boost library
include(FetchContent)
FetchContent_Declare(
  Boost
  URL https://github.com/boostorg/boost/releases/download/boost-1.82.0/boost-1.82.0.tar.xz
  URL_MD5 9ef03341798f1caf9ac910bb60cde9d6
  DOWNLOAD_EXTRACT_TIMESTAMP ON
)

set(Boost_INCLUDE_LIBRARIES system coroutine context asio beast)
FetchContent_MakeAvailable(Boost)

# Add Boost to the list of libraries
list(APPEND LIBRARIES Boost::asio Boost::system Boost::context Boost::coroutine Boost::beast)

if(BUILD_STATIC_GLIESE OR NOT BUILD_SHARED_LIBS)
  add_library(${PROJECT_NAME} STATIC ${SOURCE_FILES})
else()
  add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})
endif()
# Link the target with the libraries
target_link_libraries(${PROJECT_NAME} PRIVATE ${LIBRARIES})
# string(REPLACE "/await" "" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
# set_property(TARGET ${PROJECT_NAME} PROPERTY COMPILE_OPTIONS "/await-;/EHs-;/EH-")
# list(APPEND CMAKE_CXX_FLAGS "/await:strict")
# target_compile_options(${PROJECT_NAME} PRIVATE /await:strict)
