This was presumably created with QtDesigner. I've based this code off the code
in [this Anki
add-on](https://github.com/kelciour/batch-download-pictures-from-google-images)
with a few tweaks.

It's important that labels for the fields match the `ConfigKeys` constants in
`__init__.py`.

# Building
Before running, you need to run:
```
pyuic6 main.ui -o main.py
```

TODO: Move this into a make file or something.

