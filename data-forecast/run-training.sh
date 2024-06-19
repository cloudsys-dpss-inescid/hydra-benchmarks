#!/bin/bash

#i have tried but I have a error on the machine
#python3 -m venv pipeline-env
#source pipeline-env/bin/activate
#pip install pandas matplotlib scipy autogluon stumpy
#deactivate


rm -r AutogluonModels/*

python3 model_training.py

