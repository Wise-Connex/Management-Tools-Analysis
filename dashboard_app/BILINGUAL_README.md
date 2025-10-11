# Bilingual Dashboard Feature

This document describes the bilingual (Spanish/English) implementation for the Management Tools Analysis Dashboard.

## Overview

The dashboard now supports both Spanish and English languages, allowing users to switch between languages dynamically without page reload.

## Features

### Language Detection

- **Browser Language Detection**: Automatically detects the user's browser language on first visit
- **Fallback**: Defaults to Spanish if browser language is not supported
- **Persistence**: Remembers user's language choice using localStorage

### Language Selection

- **Flag-based Selector**: Located in the top-right corner of the header
- **Spanish Flag (🇪🇸)**: Switches to Spanish interface
- **US Flag (🇺🇸)**: Switches to English interface
- **Real-time Switching**: All UI elements update immediately when language is changed

### Content Strategy

- **Spanish Content**: Original Spanish content remains unchanged (mixed Spanish/English where appropriate)
- **English Content**: All UI elements translated to pure English
- **Tool Names**: Translated to English equivalents while maintaining database compatibility

## Technical Implementation

### Translation System

- **File**: `translations.py`
- **Dictionaries**: Separate dictionaries for Spanish (`es`) and English (`en`)
- **Function**: `get_text(key, language, **kwargs)` for parameterized translations
- **Tool Names**: `get_tool_name(tool_key, language)` for tool name translations

### Key Components

1. **Language Store**: Dash store component maintaining current language state
2. **Translation Functions**: Centralized translation system
3. **Dynamic Callbacks**: All UI elements update based on language changes
4. **Browser Integration**: JavaScript for language detection and persistence

### Supported Languages

- **Spanish (es)**: Default language
- **English (en)**: Full translation coverage

## Usage

### For Users

1. **Automatic Detection**: Dashboard detects browser language on first visit
2. **Manual Selection**: Click the flag selector in the header to switch languages
3. **Persistence**: Language choice is remembered across sessions

### For Developers

```python
from translations import get_text, get_tool_name

# Get translated text
label = get_text('select_tool', language)

# Get translated tool name
tool_name = get_tool_name('Benchmarking', language)

# Parameterized translation
title = get_text('relative_absolute', language, max_value=123.45)
```

## Translation Coverage

### UI Elements

- Sidebar labels and buttons
- Section headers and titles
- Chart labels and legends
- Modal dialogs
- Navigation elements
- Performance monitor
- Credits and licensing

### Tool Names

All management tool names have been translated to English equivalents:

- "Benchmarking" → "Benchmarking"
- "Calidad Total" → "Total Quality"
- "Gestión de Costos" → "Cost Management"
- etc.

### Chart Elements

- Axis titles
- Legend labels
- Button text
- Status messages

## Browser Language Detection

The system uses the following priority for language detection:

1. **Stored Preference**: Previously selected language from localStorage
2. **Browser Language**: `navigator.language` or `navigator.userLanguage`
3. **Fallback**: Spanish (`es`)

## Language Persistence

- **Storage**: Uses `localStorage` for client-side persistence
- **Scope**: Language preference persists across browser sessions
- **Reset**: Can be changed anytime using the flag selector

## Future Enhancements

### Potential Additions

- **More Languages**: Support for additional languages (French, German, etc.)
- **RTL Support**: Right-to-left language support if needed
- **Content Translation**: Translation of database content (notes, descriptions)
- **Voice Interface**: Language-specific voice commands

### Maintenance

- **Translation Updates**: Easy to add new translations to the dictionaries
- **Testing**: Automated tests for translation completeness
- **Validation**: Ensure all UI elements have translations

## Troubleshooting

### Common Issues

1. **Language not switching**: Check browser console for JavaScript errors
2. **Missing translations**: Verify translation keys exist in `translations.py`
3. **Tool names not updating**: Ensure callbacks include language parameter

### Debug Mode

Enable debug logging to see translation key usage:

```python
import logging
logging.getLogger('translations').setLevel(logging.DEBUG)
```

## Files Modified

### Core Files

- `app.py`: Main dashboard application with bilingual support
- `translations.py`: Translation system and dictionaries
- `tools.py`: Tool name translation support

### New Files

- `BILINGUAL_README.md`: This documentation
- `test_translations.py`: Translation system test script

## Testing

Run the translation test using UV:

```bash
cd dashboard_app
uv run python test_translations.py
```

## Compatibility

- **Browsers**: Modern browsers with localStorage support
- **Dash Version**: Compatible with current Dash installation
- **Python**: Python 3.6+ required for f-string support

## License

This bilingual implementation follows the same license as the main dashboard: CC BY-NC 4.0
