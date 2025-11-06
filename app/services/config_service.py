"""
Configuration service for loading and accessing application settings.
Implements UC6: Configuration management via YAML file.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml


class ConfigService:
    """Singleton service for application configuration."""
    
    _instance: Optional['ConfigService'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        # Look for config.yaml in project root
        config_path = Path(__file__).resolve().parents[2] / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        
        Examples:
            config.get('data_sources.weather.api_key')
            config.get('app.debug', False)
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_data_source_config(self, source: str) -> Dict[str, Any]:
        """Get configuration for a specific data source (weather, air_quality, events)."""
        config = self.get(f'data_sources.{source}', {})
        
        # Allow environment variables to override API keys
        if source == 'weather':
            env_key = os.getenv('OPENWEATHER_API_KEY')
            if env_key:
                config['api_key'] = env_key
        elif source == 'air_quality':
            env_key = os.getenv('WAQI_API_KEY')
            if env_key:
                config['api_key'] = env_key
        elif source == 'events':
            env_key = os.getenv('TICKETMASTER_API_KEY')
            if env_key:
                config['api_key'] = env_key
        
        return config
    
    def get_recommendation_config(self) -> Dict[str, Any]:
        """Get weather recommendation configuration."""
        return self.get('recommendations', {})
    
    def reload(self) -> None:
        """Reload configuration from file (useful for testing or runtime updates)."""
        self._load_config()


# Singleton instance
_config_service = ConfigService()

def get_config() -> ConfigService:
    """Get the configuration service singleton."""
    return _config_service
