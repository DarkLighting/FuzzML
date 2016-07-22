FuzzML
======

XML Fuzzer 
<br>The current release supports fuzzing by element duplication, element omission and tag malformation. Other methods may be added in the future.


*Feature requests are very welcome!*

```
usage: fuzzml.py [-h] [--no-cert-validate] [--auto]
                 [--header [<Header> [<Header> ...]] | --fheader <Header
                 file>] [--ua <User-Agent>] [--ct <Content-Type>]
                 [--data <POST content> | --fdata <POST content file>]
                 url

SOAP web service Fuzzer

positional arguments:
  url                   Web service URL to fuzz

optional arguments:
  -h, --help            show this help message and exit
  --no-cert-validate    Disable certificate validation
  --auto                Enable automatic testing
  --header [<Header> [<Header> ...]]
                        Specify required request headers
  --fheader <Headers file>
                        Specify a file containing the required request headers
  --ua <User-Agent>     Specify User-Agent header
  --ct <Content-Type>   Specify Content-Type header
  --data <POST content>
                        Data to be sent inside the request body
  --fdata <POST content file>
                        Specify a file containing the data to be sent inside
                        the request body
```

<dl>
<dt>'Header'
</dt>
<dd>is an http header you intend to be used in the request. <b>'Header'</b>, when used in command line, should be in the form 'header value' (the apostrophes should included). Note that if the strings contain any character other than letters or numbers, the word should enclosed within quotation marks. For example, if you wish to use the header "Origin: Jack's Server", you should use the string <b>'Origin "Jack's Server"'</b>(note the absence of the colon).
</dd>


<dt>'Headers File'
</dt>
<dd>is a file containing <b>'Header'</b>s, one per line. The pair header_name and value should be separated by space, but only include quotation if you intend it to be part of the header. For example, if you wish to include the header "Version: Mark/1.1", the file should contain the line <b>Version Mark/1.1</b>.
</dd>

<dt>'POST content'
</dt>
<dd>is the content you want to send to the web service. Duh.
</dd>

<dt>'POST content file'
</dt>
<dd>is a file containing data to be sent. Duh.
</dd>

<dt>'POST content'
</dt>
<dd>when in command line, <b>'POST content'</b> must be enclosed within apostrophes or quotation marks. <b>'POST content'</b> inside a <b>'POST content file'</b> file is not bound to any rule. Just put it the way you wish it to be sent.
</dd>

<dt>'User-Agent' e 'Content-Type'
</dt>
<dd>are fixed header names. Duh. If you want to change them, just provide the new values. The default values are:
</dd>
</dl>
```
Content-Type: text/xml; charset=ascii
User-Agent: FuzzML/1.0
```

All the requests and their respective responses will be saved under a folder named "requests" (created by the tool). Files will be named after the url of the web service and the time that the request was made. You will see that the pair will have the same name, except for the suffixes "req" (as in request) and "resp" (as in response).
  * `www.example.com_webservice.php_20141110_1822.15.059238_req.xml`
  * `www.example.com_webservice.php_20141110_1822.15.059238_resp.xml`

