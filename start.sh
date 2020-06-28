#!/bin/bash
sudo ionice -c3 -p$$


source .venv/bin/activate
taskset --cpu-list 4-7 python main.py
