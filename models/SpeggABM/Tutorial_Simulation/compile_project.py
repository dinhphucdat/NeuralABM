#!/home/wormlab/miniforge3/bin/python3
"""
This module helps with C++/CUDA compilation's automation. 
Responsible for creating CMakeLists.txt, build and compiling.

----------------------------------------------------------------
User's manual: 
    1. Place this file into your project's directory
    2. Optional: modify GPU_ARCH, CURAND_LIB_DIR and CUDA_LIB_DIR as needed
    3. In the terminal, type:

        $ python3 compile_project.py <your_spegg_codebase_directory> 
            <0 if only need to generate cmake, 1 if ready to build> 

-----------------------------------------------------------------
Author: Dat Dinh
*_*
"""
########### Modify ####################

CUDA_ARCH = [50, 61, 70, 75, 80, 86]  # Change this to your GPU's architecture
CURAND_LIB_DIR = "/usr/local/cuda/lib64"
CUDA_LIB_DIR = "/usr/local/cuda/lib64"
#######################################

import os
import sys
import subprocess
from pathlib import Path

if len(sys.argv) < 3:
    raise IndexError("Requires at least 2 arguments:\n----------------------------\n"
                     + "    - your GPU's architecture (etc: 61-real,...)\n" 
                     + "    - 0 if you don't want to build right away or anything else if you do\n"
                     + " ^ o ^")

SPEGG_ROOT = sys.argv[1]
IS_READY = sys.argv[2]
CURAND_DIR = CURAND_LIB_DIR if len(sys.argv) < 4 else sys.argv[3]
CUDA_DIR = CUDA_LIB_DIR if len(sys.argv) < 4 else sys.argv[4]
SHARED_OBJECT_OR_EXECUTABLE = "SHARED"  # Change this to "EXECUTABLE" if you want an executable instead of a shared object

class Bracket:
    """
    This class abstracts one group
    """
    def __init__(self, name : str, inside_brackets=None):
        self.name = name
        self.inside_brackets = list()
        if inside_brackets != None:
            if isinstance(inside_brackets, list):
                [self.inside_brackets.append(element) for element in inside_brackets]
            else:
                self.inside_brackets.append(inside_brackets)
    
    def update_bracket(self, add_into_brackets):
        if not isinstance(add_into_brackets, list):
            self.inside_brackets.append(add_into_brackets)
        else:
            [self.inside_brackets.append(element) for element in add_into_brackets]
    
    def output_string(self, sep_char="\t", base_indent=0, line_split=False) -> str:
        token = "" if not line_split else "\n"
        token_w_tab = "" if not line_split else "\n" + sep_char*(base_indent + 1)
        string = ""
        string += self.name + "(" + token_w_tab
        for element in self.inside_brackets:
            next_sep = (token + "") if element == self.inside_brackets[-1] else (" " + token_w_tab)
            string += element +  next_sep
        string += TokenManager.INDENT_SIGNATURE*base_indent + ")"
        return string

class ProjectInspector:
    """
    This class collects all source code
    """
    def __init__(self, project_path : str):
        self.project_path = project_path
        self.check_header_and_src()
        self.modules = list()
        self.collect_modules()
    
    def check_header_and_src(self):
        header_to_check = os.path.join(self.project_path, "header")
        src_to_check = os.path.join(self.project_path, "src")
        if (not os.path.exists(header_to_check)) or (not os.path.exists(src_to_check)):
            raise FileNotFoundError("[Error]: No header or src directories in project path. Aborted")
    
    def collect_modules(self):
        for root, dirs, files in os.walk(os.path.join(self.project_path, "src")):
            for file in files:
                self.modules.append(file)

class TokenManager:
    """
    Manages styles
    """
    INDENT_SIGNATURE = "\t"

    def __init__(self, initial_string=None, initial_indent=0):
        self.indent = initial_indent
        self.string = "" if initial_string == None else initial_string
    
    def add_string(self, added_str : str):
        self.string += (TokenManager.INDENT_SIGNATURE * self.indent + added_str)
    
    def decrement_indent(self):
        self.indent -= 1
    
    def increment_indent(self):
        self.indent += 1
    
    def newline(self, depth=1):
        self.string += "\n" * depth
    
    def get_string(self) -> str:
        return self.string

# JSON structure for the CMakeLists.txt
CMAKELISTS = {
    "Set the minimum version of CMake" : 
    [
        ("cmake_minimum_required", ["VERSION", "3.13"])
    ],

    "Set the independent compilation for CUDA" :
    [
        ("set", ["CMAKE_POSITION_INDEPENDENT_CODE", "ON"])
    ], 

    "Force PIC for the Python module's own source files (main.cpp)" : 
    [
        ("set", ["CMAKE_CXX_FLAGS", r"${CMAKE_CXX_FLAGS} -fPIC"])
    ], 

    "Set cuda architecture and optimization flags" : 
    [
        ("set", ["CMAKE_CUDA_FLAGS", "\""+r"${CMAKE_CUDA_FLAGS} -Xcompiler -fPIC -O3 --extended-lambda --expt-relaxed-constexpr"+"\""]), 
        ("set", ["CMAKE_CUDA_ARCHITECTURES"] + [str(el) for el in CUDA_ARCH])
    ], 

    "Set the project's name" : 
    [
        ("project", [os.path.basename(Path(".").resolve()), "LANGUAGES", "CXX", "CUDA"])
    ],

    "Set cuda, curand paths" : 
    [
        ("set", ["CURAND_DIR", CURAND_DIR]), 
        ("set", ["CUDA_DIR", CUDA_DIR])
    ],

    "Import code base" : 
    [
        ("if", ["NOT", "SPEGG_ROOT"]),
        ("->", [
            ("set", ["SPEGG_ROOT", os.path.abspath(SPEGG_ROOT)]), 
            ("list", ["APPEND", "CMAKE_MODULE_PATH", r"${SPEGG_ROOT}", True])
        ]),
        ("endif", [])
    ], 

    "Add cmake" : 
    [
        ("include", r"${SPEGG_ROOT}/FindSPEGG.cmake")
    ],

    "Find CUDA and SPEGG packages" : [
        ("find_package", ["CUDA", "REQUIRED"]),
        ("find_package", ["SPEGG", "REQUIRED"])
    ], 

    "Set where the binary would go" :
    [
        ("set", ["CMAKE_RUNTIME_OUTPUT_DIRECTORY", r"${CMAKE_SOURCE_DIR}"])
    ],

    "Add include dirs" : 
    [
        ("include_directories", r"${CMAKE_SOURCE_DIR}/header"), 
        ("include_directories", r"${SPEGG_INCLUDE_DIRS}"), 
        ("include_directories", r"${CUDA_INCLUDE_DIRS}")
    ], 

    "Define src directory" : 
    [
        ("set", ["SRC", r"${CMAKE_SOURCE_DIR}/src"])
    ], 

    "Add static library" : 
    [
        ("add_library", ["sim_static", "STATIC"] + 
            [(r"${SRC}/" + module) for module in ProjectInspector(".").modules] + 
            [True])
    ], 

    f"Add {SHARED_OBJECT_OR_EXECUTABLE}" : 
    [
        ("pybind11_add_module", [r"${PROJECT_NAME}", r"main.cpp"]) 
            if SHARED_OBJECT_OR_EXECUTABLE == "SHARED" else 
        ("add_executable", [r"${PROJECT_NAME}", r"main.cpp"])
    ], 

    "This is the \"Double-Lock\"":
    [
        ("target_compile_options", ["sim_static", "PRIVATE",  
            r"$<$<COMPILE_LANGUAGE:CXX>:-fPIC>", 
            r"$<$<COMPILE_LANGUAGE:CUDA>:-Xcompiler -fPIC>"]
        )
    ],

    "Enable separable compilation for all CUDA targets" : 
    [
        ("set_target_properties", [
            r"${PROJECT_NAME}", 
            "PROPERTIES", 
            "CUDA_SEPARABLE_COMPILATION ON", 
            "CUDA_RESOLVE_DEVICE_SYMBOLS ON", 
            "POSITION_INDEPENDENT_CODE ON", 
            "CXX_VISIBILITY_PRESET default",
            "CUDA_VISIBILITY_PRESET default",
            "VISIBILITY_INLINES_HIDDEN OFF", 
            "LINKER_LANGUAGE CUDA",  
	        "CUDA_RUNTIME_LIBRARY Shared"
        ] + [True])
    ], 

    "Target link to the executable" : 
    [
        ("target_link_libraries", [
            "sim_static", 
            "PRIVATE", 
            "SPEGG::spegg_codebase"
        ] + [True])
    ], 

    "Final linking with curand and cuda libraries" :
    [
        ("target_link_libraries", [
	        r"${PROJECT_NAME}",  
            "PRIVATE", 
            "-Wl,--whole-archive sim_static SPEGG::spegg_codebase -Wl,--no-whole-archive", 
            r"${CUDA_LIBRARIES}", 
            "cudart", 
            "curand"] + [True]
        )
    ]
}

def write_cmake_group(content : list, style_manager : TokenManager):
    """
    Write the group (value) with the key as the comment
    """
    for command, params in content:
        # The case where there is an indentation
        if command == "->":
            # Increment the indentation in the buffer
            style_manager.increment_indent()
            # Process this function recursively since the value is another dict
            write_cmake_group(params, style_manager)
            # Make sure to roll the token back when done with that indentation
            style_manager.decrement_indent()
        else:
            par_list = params if (len(params) == 0 or params[-1] != True) else params[:-1]
            br = Bracket(command, par_list)
            line_split = False if (len(params) == 0 or params[-1] != True) else True
            style_manager.add_string(br.output_string(
                sep_char=TokenManager.INDENT_SIGNATURE, 
                base_indent=style_manager.indent, 
                line_split=line_split))
            style_manager.newline()
            del br

def write_cmake(cmake_json : dict) -> str:
    """
    write cmake into the buffer and return it
    """
    style_manager = TokenManager()
    for key, value in cmake_json.items():
        style_manager.add_string("# " + key + "\n")
        write_cmake_group(value, style_manager)
        style_manager.newline()
    return style_manager.get_string()


string = write_cmake(
    CMAKELISTS
)

with open(f"CMakeLists.txt", "w") as f:
    f.write(string)

isReady = IS_READY != "0"

if isReady:
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Run the `cmake ..` command in the build directory
    try:
        subprocess.run(["cmake", ".."], cwd="build", check=True)
        print("CMake configuration completed successfully.")

        subprocess.run(["make"], cwd="build", check=True)
        print("Build completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running `cmake ..`: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
