# PDF-and-CSV-to-HL7
Generates HL7 from PDF files and CSV rows

## Instructions

Change these values to match your paths:

```python
source_path = "PDF_PATH"
destination_path = "DESTINATION_FILE"
data_path = "CSV_PATH"
```

And run! It will generate an individual HL7 file per record.

## Dependancies

```python
import base64
import pandas
import csv
import numpy
from dateutil import parser
from datetime import datetime
```

## Credits

Created by [David Crawford](https://github.com/DaveAldon)
