# Work Timer

Based on 90-minute work periods followed by 20-minute rest periods. This work schedule was suggested by Dr. Andrew Huberman for higher levels of focus during work periods, as well as improved recovery during break periods.

Developed and tested on Windows. Some of the notifications and sounds are likely to break on other operating systems.

## Generating an .exe file

Based on [this video](https://www.youtube.com/watch?v=UZX5kH72Yx4).

To generate `main.exe` run the following in `daily_timer/` using Git Bash (commands will be different using Windows commandline or Powershell):

```bash
pyinstaller --onefile main.py
mv dist/main.exe .
rm -rf build
rm -rf dist
rm main.spec
```

Then double click on `main.exe` to start the timer.
