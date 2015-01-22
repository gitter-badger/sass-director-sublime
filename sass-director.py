import os
import re
import sublime
import platform
import sublime_plugin


class Sassdirectorgenerate(sublime_plugin.WindowCommand):
    # Global Vars
    root_path = ""
    manifest_path = ""
    manifest_file = ""
    prune_list = [';', '@import', '\'', '\"']

    def defineRoot(self):
        """Function defineRoot
        @Parameters: None

        Defines the Root Path and Files/Directories in the Root
        """
        folders = self.window.folders()
        view = self.window.active_view()
        # Map Dirs + Files
        self.root_path = folders[0]
        self.manifest_file = view.file_name()
        # Detect the OS
        if(platform.system() is "Windows"):
            self.manifest_path = self.manifest_file[:self.manifest_file.rfind('\\')]
        else:
            self.manifest_path = self.manifest_file[:self.manifest_file.rfind('/')]

    def pruneImport(self, line):
        """Function pruneImport
        @Parameters line: {str}

        Removes unnecessary information from the line
        """
        for delimeter in self.prune_list:
            line = line.replace(delimeter, '')
        return line.strip()

    @staticmethod
    def expandImports(imports):
        """Function expandImports
        @Parameters imports: {List}

        Expands the list of imports into an array of strings. Each entry in the
        array is like follows:

        ['{root_folder}', '{folder_in_root_folder}', ... , 'filename']
        """
        paths = []
        for e in imports:
            # Split the structure
            path = e.split('/')
            paths.append(path)
        return paths

    def generateDirectories(self, dirs, view):
        # Each entry is a directory structure
        for d in dirs:
            file_name = '_' + d.pop(len(d)-1)
            os.chdir(self.manifest_path)
            for directory in d:
                if directory not in os.listdir('.'):
                    os.mkdir(directory)
                    os.chdir(directory)
                    print("Made directory:", directory)
                    print("Now at:", os.path.dirname(os.path.realpath(__file__)))
                else:
                    os.chdir(directory)
                    print("Directory already exists")
            # Navigate to endpoint via dir
            os.chdir(self.manifest_path)
            for directory in d:
                os.chdir(directory)
            # Change to associated directory
            f = open(file_name + '.scss', 'w')
            print("Wrote new scss file:", file_name)
            f.close()

    def run(self):
        self.defineRoot()
        view = self.window.active_view()
        body = view.substr(sublime.Region(0, view.size()))
        lines = body.split('\n')

        imports = []
        # Grab Import Lines
        for line in lines:
            if re.match('^@import', line):
                imports.append(self.pruneImport(line))
        dirs = self.expandImports(imports)
        self.generateDirectories(dirs, view)
        print("Done! Refreshing folder list...")
        view.run_command('refresh_folder_list')
