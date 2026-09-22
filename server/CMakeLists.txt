cmake_minimum_required(VERSION 3.20)
project(avesta74 CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")

find_package(Boost REQUIRED COMPONENTS thread regex)
find_package(LibXml2 REQUIRED)
find_package(unofficial-sqlite3 CONFIG REQUIRED)
find_path(GMP_INCLUDE_DIR gmp.h REQUIRED)
find_library(GMP_LIBRARY NAMES gmp libgmp REQUIRED)
find_path(LUAJIT_INCLUDE_DIR luajit.h PATH_SUFFIXES luajit REQUIRED)
find_library(LUAJIT_LIBRARY NAMES lua51 luajit REQUIRED)

file(GLOB SOURCES CONFIGURE_DEPENDS src/*.cpp)
# MySQL driver is not used (SQLite only)
list(FILTER SOURCES EXCLUDE REGEX "databasemysql\.cpp$")

add_executable(avesta74 ${SOURCES})
target_include_directories(avesta74 PRIVATE src ${LUAJIT_INCLUDE_DIR} ${GMP_INCLUDE_DIR})
target_compile_definitions(avesta74 PRIVATE
  __USE_SQLITE__
  BOOST_BIND_GLOBAL_PLACEHOLDERS
  _CRT_SECURE_NO_WARNINGS
  _WINSOCK_DEPRECATED_NO_WARNINGS
  NOMINMAX
  _HAS_AUTO_PTR_ETC=1
)
if(MSVC)
  target_compile_options(avesta74 PRIVATE /W1 /MP /bigobj /permissive)
endif()
target_link_libraries(avesta74 PRIVATE
  Boost::thread Boost::regex
  LibXml2::LibXml2
  unofficial::sqlite3::sqlite3
  ${LUAJIT_LIBRARY}
  ${GMP_LIBRARY}
  ws2_32 mswsock winmm
)

# Put the exe next to config.lua and data/
set_target_properties(avesta74 PROPERTIES
  RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}"
  RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}"
  RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}"
)
