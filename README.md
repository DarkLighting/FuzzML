FuzzML
======

XML Fuzzer (still under development)

```
usage: fuzzml.py [-h] [--no-cert-validate] [--auto]
                 [--header [HEADER [HEADER ...]] | --fheader FHEADER]
                 [--ua UA] [--ct CT] [--data DATA | --fdata FDATA]
                 url

SOAP web service Fuzzer

positional arguments:
  url                   Web service URL to fuzz

optional arguments:
  -h, --help            show this help message and exit
  --no-cert-validate    Disable certificates validation
  --auto                Enable automatic testing
  --header [HEADER [HEADER ...]]
                        Specify required request headers
  --fheader FHEADER     Specify a file containing the required request headers
  --ua UA               Specify User-Agent header
  --ct CT               Specify Content-Type header
  --data DATA           Data to be sent inside the request body
  --fdata FDATA         Specify a file containing the data to be sent inside
                        the request body
```
