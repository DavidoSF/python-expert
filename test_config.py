"""Quick test to verify configuration loading works."""
try:
    from app.services.config_service import get_config
    
    config = get_config()
    
    print("✓ Configuration loaded successfully")
    print(f"✓ App name: {config.get('app.name')}")
    print(f"✓ Weather provider: {config.get('data_sources.weather.provider')}")
    print(f"✓ Air quality provider: {config.get('data_sources.air_quality.provider')}")
    print(f"✓ Events provider: {config.get('data_sources.events.provider')}")
    print(f"✓ Confidence threshold: {config.get('recommendations.confidence_threshold')}")
    
    # Test data source config retrieval with env var override
    weather_config = config.get_data_source_config('weather')
    print(f"✓ Weather API key loaded: {weather_config['api_key'][:10]}...")
    
    print("\n✅ Configuration system working correctly!")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    import traceback
    traceback.print_exc()
