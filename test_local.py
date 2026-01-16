import sys
sys.path.append('lambda/scanners')
from ebs_scanner import lambda_handler

# Run the scanner
result = lambda_handler({}, {})
print(result)