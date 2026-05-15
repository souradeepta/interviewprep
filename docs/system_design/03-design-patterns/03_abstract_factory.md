# Abstract Factory Pattern

## Overview
Creates families of related objects without specifying concrete classes.

## Problem Statement
System needs to work with multiple families of related products (e.g., themes, UI kits, database families). Tight coupling to concrete classes. Adding new family requires changing code everywhere.

## Solution
Create abstract factory for each family. Concrete factories create related objects together.

## When to Use

**Use Abstract Factory when:**
- Multiple families of related objects (UI themes, database providers)
- Objects created together (Button + Checkbox for same theme)
- Families may be swapped at runtime (light/dark theme)
- Ensure consistency within family (don't mix Windows + Mac UI)

**Examples:**
- UI Toolkit: create Button, Checkbox, Textbox for Windows or Mac
- Database abstraction: PostgreSQL, MySQL, SQLite all have Connection, Statement, ResultSet
- Cloud providers: AWS, Azure, GCP all have VM, Storage, Database services
- Document formats: PDF, Word, HTML factories create Document, Paragraph, Table

## Real-World Scenarios

**UI Theme Factory:**
```
Application supports Light and Dark themes
Each theme needs Button, Checkbox, Window implementations
LightThemeFactory creates light Button, light Checkbox, light Window
DarkThemeFactory creates dark Button, dark Checkbox, dark Window
Client code uses factory, never knows concrete classes
```

**Cloud Provider Factory:**
```
System deployable on AWS, Azure, or GCP
Each provider has VM, Storage, Database services
AwsFactory creates EC2 (VM), S3 (Storage), RDS (Database)
AzureFactory creates VirtualMachine, BlobStorage, CosmosDB
Single client code, swappable providers
```

## When NOT to Use

**Avoid when:**
- Single family (factory method sufficient)
- Objects not related (no family concept)
- Static configuration (no need to swap families)

## Implementation Patterns

### UI Theme Example
```python
class Button:
    pass

class Checkbox:
    pass

class LightButton(Button):
    def render(self):
        return "Light Button"

class DarkButton(Button):
    def render(self):
        return "Dark Button"

class UIFactory:
    def create_button(self) -> Button:
        pass

    def create_checkbox(self) -> Checkbox:
        pass

class LightThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_checkbox(self) -> Checkbox:
        return LightCheckbox()

class DarkThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return DarkButton()
```

## Trade-Offs

**Pros:**
- Encapsulates related objects (consistency)
- Easy to swap families (single factory change)
- Add new family without modifying existing code
- Prevents mixing incompatible objects

**Cons:**
- Complex (many classes and interfaces)
- Extending families requires changing abstractions
- Harder to understand than factory method
- Overkill if families small or simple

## Production Considerations

- Use dependency injection to provide factory
- Document family relationships (which objects belong together)
- Make factory immutable once created (prevent runtime inconsistency)
- Consider registry pattern for dynamic family registration
- Monitor which families used (feature usage analytics)
