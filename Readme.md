# Seedrs Crowdfunding Tracker



## Getting Started with development

to install the required dependencies and configure your virtual env: 
```
pip install pipenv # install pipenv to manage deps in an easy way
pipenv install # install virtual env, and install required deps
pipenv shell # load virtual env
python ./YatterNotifier.py
```
### Prerequisites for using source code

You must have python 3.6 > installed.

You can use the manual dependencies too if you don't want to use pipenv:
```
# install dependencies
pip install pypiwin32 pyttsx3 plyer lxml cx_Freeze
# execute the tool
python3 ./YatterNotifier.py
```
### Installing

A published build is available, I will release the URL soon.

## Platform support

Tested on:
* Windows 10
* Windows 7

### Note on platform support:
Windows 7 doesn't have notifications, therefore you may need to change the configuration file and just enable "play_sound", which will use text to speech and tell you the detailed amount when the investment amount changes.

### Testing

Inside the YatterNotifier.py change Debugging=False to Debugging=True, this forces it to believe their is a change in, investment.

## Deployment
To build this into an executable run:
```
python setup.py build
```
**Note:** windows 7 has an issue, where you need to copy the "VCRUNTIME140.dll" from the build/exe.win32-3.6/lib folder, into the folder where the exe is, e.g. in build/exe.win32-3.6/.

for more information on exe packaging, please look at [cx_Freeze](http://cx-freeze.readthedocs.io/en/latest/index.html)

## Built With

* [cx-freeze](http://cx-freeze.readthedocs.io/en/latest/index.html) - For packaging
* [Python 3.6](https://www.python.org/) - Programming language
* [Pyttsx3](https://pypi.python.org/pypi/pyttsx3/2.6) - Text to speech synthesis
* [win32](https://pypi.python.org/pypi/pypiwin32/220) - Windows 32 API access
* [playsound](https://pypi.python.org/pypi/playsound) - For playing sounds when investment is found
* [plyer](https://pypi.python.org/pypi/plyer/1.3.0) - Platform Notifications

## Authors

* **Gordon MacPherson** - *Software Development* - [RevoluPowered](https://github.com/RevoluPowered)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
* Seedrs crowdfunding platform, thanks for your well structured site.
* Fellow python developers, thank you for your support.
* My Colleagues at yatter, thanks for the good banter.
* Stackoverflow, thank you for your support over the past few years.
