from conan import ConanFile
from conan import tools
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.microsoft import VCVars
from conans.errors import ConanInvalidConfiguration
import os

class Gliese(ConanFile):
    name = "Gliese"
    version = "1.0"
    settings = "os", "compiler", "build_type", "arch"
    exports_source = "*.patch"
    exports_sources = "CMakeLists.txt", "src/*", "include/*"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}
    cppstd = "20"
    generators = "CMakeDeps"
    def __init__(self, display_name="Kepler"):
        super().__init__(display_name)
        self.current_dir = os.path.dirname(__file__)
        self.libraries = {}
        with open(os.path.join(self.current_dir,"ConanLibraries.txt"), "r+") as file:
            for string in file.readlines():
                library,type = string.replace("\n","").split(":")[0],string.replace("\n","").split(":")[1]
                self.libraries.update({library:type})

    def configure(self):
        for library,type in self.libraries.items():
            library = library.split("/")[0]
            if type == "shared":
                self.options[library].shared = True
            elif type == "static":
                self.options[library].shared = False
            else:
                raise ConanInvalidConfiguration(f"Invalid build type of {library}")
        # self.options["fmt/11.0.2"].shared = True
        # self.options["andreasbuhr-cppcoro/cci.20230629"].shared = True
        # self.options["jsoncpp/1.9.5"].shared = True
        # self.options["openssl/3.3.1"].shared = True
        # self.options["zlib/1.3.1"].shared = True

    def generate(self):
        tc = CMakeToolchain(self,generator="Ninja")
        tc.generate()
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)
        
    def source(self):
        print("Cloning Gliese")
        src_dir = os.path.join(self.source_folder,"src")
        git = tools.Git(src_dir)
        git.clone("https://github.com/DeepForge-Tech/Gliese")

        print("Checkout Gliese")
        commit = self.conan_data["versions"][self.version]
        git.checkout(commit)

        print("Patching Gliese")
        patches = self.conan_data["patches"][self.version]

        src_patch_files = []
        for patch in patches:
            src_patch_files.append(os.path.join(self.source_folder,patch))

        print("Applied patches")
        for src_patch_file in src_patch_files:
            tools.patch(patch_file=src_patch_file,base_path=src_dir)
            print(src_patch_file)

    def requirements(self):
        self.requires("fmt/11.0.2")
        self.requires("andreasbuhr-cppcoro/cci.20230629")
        self.requires("jsoncpp/1.9.5")
        self.requires("openssl/3.3.1")
        self.requires("zlib/1.3.1")
        # self.requires("boost/1.86.0")
    
    def build(self):
        print("Building Gliese")
        src_dir = os.path.join(self.source_folder,"src")
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        cmake.configure(source_folder=src_dir)
        cmake.build(target="Gliese")
    
    def package(self):
        print("Packaging Gliese")
        self.copy("*.hpp",dst="include",keep_path=False)
        self.copy("*.h",dst="include",keep_path=False)
        self.copy("*.lib",dst="lib",keep_path=False)
        self.copy("*.a",dst="lib",keep_path=False)
        self.copy("*.so",dst="lib",keep_path=False)
        self.copy("*.dylib",dst="lib",keep_path=False)
        self.copy("*.dll",dst="lib",keep_path=False)
    
    def package_info(self):
        print("Package Info")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libs = ["Gliese"]
        self.cpp_info.system_libs.append("zlib")
