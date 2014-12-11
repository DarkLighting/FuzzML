FuzzML
======

XML Fuzzer 
<br>The current release supports fuzzing by element duplication, element omission and tag malformation. Other methods will be added in the future.


*Feature requests are very welcome!*

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

* 'HEADER' is an http header you intend to be used in the request. 'HEADER', when used in command line, should be in the form 'header value' (the apostrophes should included). Note that if the strings contain any character other than letters or numbers, the word should enclosed within quotation marks. For example, if you wish to use the header "Origin: Jack's Server", you should use the string ```'Origin "Jack's Server"'```(note the absence of the colon).

* 'FHEADER' is a file containing 'HEADER's, one per line. The pair header_name and value should be separated by space, but only include quotation if you intend it to be part of the header. For example, if you wish to include the header "Version: Mark/1.1", the file should contain the line ```Version Mark/1.1```.

* 'DATA' is the content you want to send to the web service.

* 'FDATA' is a file containing data to be sent.

* 'DATA', when in command line, must be enclosed within apostrophes or quotation marks. 'DATA' inside an 'FDATA' file is not bound to any rule. Just put it the way you wish it to be sent.

* 'UA' e 'CT' are fixed header names. If you want to change them, just provide the new values. The default values are:
```
Content-Type: text/xml; charset=ascii
User-Agent: FuzzML/1.0
```

All the requests and their respective responses will be saved under a folder named "requests" (created by the tool). Files will be named after the url of the web service and the time that the request was made. You will see that the pair will have the same name, except for the suffixes "req" (as in request) and "resp" (as in response).
  * `www.example.com_webservice.php_20141110_1822.15.059238_req.xml`
  * `www.example.com_webservice.php_20141110_1822.15.059238_resp.xml`

