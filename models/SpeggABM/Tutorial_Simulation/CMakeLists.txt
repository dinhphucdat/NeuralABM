# Set the minimum version of CMake
cmake_minimum_required(VERSION 3.13)

# Set the independent compilation for CUDA
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Force PIC for the Python module's own source files (main.cpp)
set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} -fPIC)

# Set cuda architecture and optimization flags
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -Xcompiler -fPIC -O3 --extended-lambda --expt-relaxed-constexpr")
set(CMAKE_CUDA_ARCHITECTURES 50 61 70 75 80 86)

# Set the project's name
project(Tutorial_Simulation LANGUAGES CXX CUDA)

# Set cuda, curand paths
set(CURAND_DIR /usr/local/cuda/lib64)
set(CUDA_DIR /usr/local/cuda/lib64)

# Import code base
if(NOT SPEGG_ROOT)
	set(SPEGG_ROOT /home/wormlab/datdinh_server/NeuralABM/models/SpeggABM/spegg	)
	list(
		APPEND 
		CMAKE_MODULE_PATH 
		${SPEGG_ROOT}
	)
endif()

# Add cmake
include(${SPEGG_ROOT}/FindSPEGG.cmake)

# Find CUDA and SPEGG packages
find_package(CUDA REQUIRED)
find_package(SPEGG REQUIRED)

# Set where the binary would go
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})

# Add include dirs
include_directories(${CMAKE_SOURCE_DIR}/header)
include_directories(${SPEGG_INCLUDE_DIRS})
include_directories(${CUDA_INCLUDE_DIRS})

# Define src directory
set(SRC ${CMAKE_SOURCE_DIR}/src)

# Add static library
add_library(
	sim_static 
	STATIC 
	${SRC}/genotype_phenotype_map.cu 
	${SRC}/Penguins.cu 
	${SRC}/UpdateBehavior.cu 
	${SRC}/Penguins_genotype_phenotype_maps.cu 
	${SRC}/update_Penguins.cu 
	${SRC}/Penguin_Parents.cu 
	${SRC}/Penguin_Drift_Simulator.cu
)

# Add SHARED
pybind11_add_module(${PROJECT_NAME} main.cpp)

# This is the "Double-Lock"
target_compile_options(sim_static PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-fPIC> $<$<COMPILE_LANGUAGE:CUDA>:-Xcompiler -fPIC>)

# Enable separable compilation for all CUDA targets
set_target_properties(
	${PROJECT_NAME} 
	PROPERTIES 
	CUDA_SEPARABLE_COMPILATION ON 
	CUDA_RESOLVE_DEVICE_SYMBOLS ON 
	POSITION_INDEPENDENT_CODE ON 
	CXX_VISIBILITY_PRESET default 
	CUDA_VISIBILITY_PRESET default 
	VISIBILITY_INLINES_HIDDEN OFF 
	LINKER_LANGUAGE CUDA 
	CUDA_RUNTIME_LIBRARY Shared
)

# Target link to the executable
target_link_libraries(
	sim_static 
	PRIVATE 
	SPEGG::spegg_codebase
)

# Final linking with curand and cuda libraries
target_link_libraries(
	${PROJECT_NAME} 
	PRIVATE 
	-Wl,--whole-archive sim_static SPEGG::spegg_codebase -Wl,--no-whole-archive 
	${CUDA_LIBRARIES} 
	cudart 
	curand
)

