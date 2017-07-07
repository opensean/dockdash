#!/usr/bin/env python3
__author__ = "Sean Landry"
__github__= "opensean"
__version__= "0.0.1"
__date__= "2017jul06"
__status__ = "development"
__description__= "simple dashboard for docker containers"

import subprocess
import logging
import yaml
import os

class DockDash():

    def __init__(self, containers = None, 
                 log = logging.INFO):

        self.logger = self.init_logger(log)
        self.logger.debug("logger intialized")
        self.containers = self.inspect_containers(containers = containers)
        self.config_path = os.path.join(os.environ.get('HOME'), 
                           ".tmuxinator/dockdash.yml")
        self.config = self.build_config(containers = self.containers)

    def init_logger(self, log = logging.DEBUG):
        rootLogger = logging.getLogger()
        class_logger = logging.getLogger(self.__class__.__name__)
            
        ## change root logger level if not equal to log arg, necessary if 
        ## working with this class in ipython session, logging library uses
        ## a hierarchy structure meaning child loggers will pass args to 
        ## parent first, root loggers default level is 30 (logging.WARNING),
        ## need to set root logger to log arg level to allow child logger a 
        ## chance to handle log output
        if rootLogger.level != log:
            logging.basicConfig(level = log)

        class_logger.setLevel(log)
        return class_logger

    def build_config(self, containers = None):
        """
        Creates a dictionary that can be used to configure a tmuxinator 
        project.

        Args:
            containers (lst): a list of containers names or numerical IDs.

        Returns:
            config (dict): in tmuxinator format.

        yaml.dump() with create a tmuxinator .yml template with the 
        following format:

        # ~/.tmuxinator/dockdash.yml

        name: dockdash
        root: ~/
        windows:
        - dockdash:
            layout: tiled
            panes:
                - docker attach container_name

        """
        self.logger.debug("building tmuxinator dockdash.yml")
        config = {}
        config["name"] = "dockdash"
        config["root"] = "~/"
        config["windows"] = [{"dockdash": {"layout": "tiled", "panes":[]}}]
        attach = "docker attach"
        p = config['windows'][0]['dockdash']['panes']
        for c in containers:
            p.append(" ".join((attach, c)))
        return config 


    def inspect_containers(self, containers = None):
        """
        Find all running containers if none are specified.

        Args:
            containers (lst): a list of container names or numerical IDs.
        
        Returns:
            containers (lst): a list of container names or numerical IDs.
        """
        self.logger.debug("inspecting containers")
        if containers:
            return containers
        else:
            proc = subprocess.Popen(["docker", "ps", "-a", "-q"], 
                                 stdout = subprocess.PIPE)
            return [c for c in proc.communicate()[0].decode().strip().split('\n')]

    def run(self):
        """
        Start the tmuxinator project.

        """
        self.logger.info('starting dockdash')
        with open(self.config_path, "w") as cOUT:
            yaml.dump(self.config, cOUT)
        argLst = ["tmuxinator", "start", "dockdash"]
        subprocess.run(argLst)
