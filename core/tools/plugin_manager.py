"""
Plugin Manager for Dawn Framework.

This module provides functionality to discover, load, and manage tool plugins.
"""

import importlib
import inspect
import os
import pkgutil
import sys
from typing import Dict, List, Optional, Set, Type

from core.tools.plugin import ToolPlugin


class PluginManager:
    """
    Manages the discovery, loading, and registration of tool plugins.
    """  # noqa: D202

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: Dict[str, ToolPlugin] = {}
        self.plugin_classes: Dict[str, Type[ToolPlugin]] = {}
        self.registered_namespaces: Set[str] = set()

    def discover_plugins(self, package_name: str) -> List[Type[ToolPlugin]]:
        """
        Discover all tool plugin classes in a package.
        
        Args:
            package_name: The name of the package to scan for plugins
            
        Returns:
            List of discovered plugin classes
        """
        discovered_plugins = []
        
        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__
            prefix = package.__name__ + "."
            
            for _, module_name, is_pkg in pkgutil.iter_modules(package_path, prefix):
                # Skip packages, only consider modules
                if is_pkg:
                    continue
                    
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find all classes in the module that are subclasses of ToolPlugin
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, ToolPlugin) and 
                            obj is not ToolPlugin and 
                            not inspect.isabstract(obj)
                        ):
                            discovered_plugins.append(obj)
                            
                except ImportError as e:
                    print(f"Error importing module {module_name}: {e}")
                except Exception as e:
                    print(f"Error processing module {module_name}: {e}")
        
        except ImportError as e:
            print(f"Error importing package {package_name}: {e}")
        except Exception as e:
            print(f"Error discovering plugins in package {package_name}: {e}")
            
        return discovered_plugins
    
    def register_plugin_namespace(self, namespace: str) -> None:
        """
        Register a namespace (package) where plugins can be found.
        
        Args:
            namespace: The package namespace to register
        """
        if namespace not in self.registered_namespaces:
            self.registered_namespaces.add(namespace)
    
    def load_plugins(self, reload: bool = False) -> None:
        """
        Load all plugins from registered namespaces.
        
        Args:
            reload: Whether to reload already loaded plugins
        """
        for namespace in self.registered_namespaces:
            plugin_classes = self.discover_plugins(namespace)
            
            for plugin_class in plugin_classes:
                plugin_instance = plugin_class()
                tool_name = plugin_instance.tool_name
                
                # Skip already loaded plugins unless reload is True
                if tool_name in self.plugins and not reload:
                    continue
                    
                self.plugins[tool_name] = plugin_instance
                self.plugin_classes[tool_name] = plugin_class
                
                # Register aliases
                for alias in plugin_instance.tool_aliases:
                    if alias not in self.plugins or reload:
                        self.plugins[alias] = plugin_instance
    
    def load_plugins_from_namespace(self, namespace: str, options: dict) -> None:
        """
        Load plugins from a specific namespace.
        
        Args:
            namespace: The namespace to load plugins from
            options: Additional options for loading plugins
            
        Raises:
            ValueError: If the namespace does not exist or is not a valid package
        """
        if not namespace or not isinstance(namespace, str):
            raise ValueError(f"Invalid namespace: {namespace}")
            
        # Check if the namespace exists as a Python package
        try:
            # This will raise ImportError if the namespace doesn't exist
            importlib.import_module(namespace)
        except ImportError as e:
            # Convert ImportError to ValueError with a clearer message
            error_msg = f"Namespace '{namespace}' does not exist or is not a valid Python package: {str(e)}"
            raise ValueError(error_msg) from e
        except Exception as e:
            # Handle other exceptions that might occur during import
            error_msg = f"Error importing namespace '{namespace}': {str(e)}"
            raise ValueError(error_msg) from e
            
        # Register the namespace if it's valid
        self.register_plugin_namespace(namespace)
        
        # Discover and load plugins from this namespace
        plugin_classes = self.discover_plugins(namespace)
        
        for plugin_class in plugin_classes:
            plugin_instance = plugin_class()
            tool_name = plugin_instance.tool_name
            
            self.plugins[tool_name] = plugin_instance
            self.plugin_classes[tool_name] = plugin_class
            
            # Register aliases
            for alias in plugin_instance.tool_aliases:
                self.plugins[alias] = plugin_instance
    
    def get_plugin(self, name: str) -> Optional[ToolPlugin]:
        """
        Get a plugin by name.
        
        Args:
            name: The name of the plugin to get
            
        Returns:
            The plugin instance if found, None otherwise
        """
        return self.plugins.get(name)
    
    def get_all_plugins(self) -> Dict[str, ToolPlugin]:
        """
        Get all registered plugins.
        
        Returns:
            Dictionary mapping plugin names to plugin instances
        """
        return self.plugins
    
    def get_plugin_metadata(self) -> List[Dict]:
        """
        Get metadata for all registered plugins.
        
        Returns:
            List of dictionaries containing plugin metadata
        """
        unique_plugins = set(self.plugins.values())
        return [plugin.get_metadata() for plugin in unique_plugins] 