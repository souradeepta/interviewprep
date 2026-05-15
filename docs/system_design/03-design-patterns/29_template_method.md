# Template Method Pattern

## Overview
Defines algorithm skeleton in base class. Subclasses provide specific steps.

## Problem Statement
Multiple classes with similar algorithms but different details. Duplicate code.

## Solution
Define template method with algorithm skeleton. Subclasses override specific steps.

## When to Use

**Use Template Method when:**
- Multiple classes with similar algorithms
- Common algorithm, varying implementations
- Avoid code duplication
- Control where subclasses can override (template method controls flow)

**Examples:**
- Data processing (read → parse → validate → save)
- Report generation (fetch data → format → render → export)
- Build process (compile → test → package → deploy)
- Game initialization (load assets → init entities → start game)

## Real-World Scenarios

**Report Generation:**
```
Base: ReportGenerator
  1. fetchData()
  2. formatData()
  3. renderReport()
  4. exportReport()

Subclasses: PdfReport, ExcelReport, HtmlReport
Override specific steps
Same structure, different implementations
```

## Implementation Patterns

### Template Method Example
```python
class DataProcessor:
    def process(self):
        # Template method
        data = self.read_data()
        data = self.parse_data(data)
        data = self.validate_data(data)
        self.save_data(data)

    def read_data(self):
        pass

    def parse_data(self, data):
        pass

    def validate_data(self, data):
        pass

    def save_data(self, data):
        pass

class CsvProcessor(DataProcessor):
    def read_data(self):
        return "CSV data"

    def parse_data(self, data):
        return data.split(',')

    def validate_data(self, data):
        return True

    def save_data(self, data):
        print("Saved to database")

# Usage
processor = CsvProcessor()
processor.process()
```

## Trade-Offs

**Pros:** Eliminate duplication, control flow in base class, code reuse

**Cons:** Subclasses limited (can only override hooks), rigid structure

## Production Considerations

- Use hooks for extension points (protected methods)
- Document which methods to override
- Validate overrides (preconditions, postconditions)
