#Can I Make Coffee ?

### What is it ?:
This is a simple little camera based movement detector. Specially designed to detect if the 42 coffee machine are free.

### How it works ?:
It's based on scam.42.fr (so you can't use it outside of 42). And OpenCV library for movement detection.

### Demo:
![coffee3](https://cloud.githubusercontent.com/assets/8771783/20031916/ea8af6a6-a37f-11e6-8279-45005bd6f39c.gif)

## Installation:

### Requirements:
- python3
- pip
- virtualenv

### How to:
    # Git clone the project
    git clone https://github.com/avallete/CanIMakeCoffee.git; cd CanIMakeCofee
    # Create and activate virtualenv
    virtualenv --python=python3 venv; source venv/bin/activate
    # Install project requirements
    pip install -r requirements.txt
    # Run the script
    python ./coffee_monitor.py

## License
Copyright © 2016 Valleteau Andrew <avallete@student.42.fr>

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar.

See the license.txt file for more details.
