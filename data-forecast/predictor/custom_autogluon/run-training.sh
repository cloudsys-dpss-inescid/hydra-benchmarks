#!/bin/bash

#i have tried but I have a error on the machine
#python3 -m venv pipeline-env
#source pipeline-env/bin/activate
#pip install pandas matplotlib scipy autogluon stumpy
#deactivate

#I do not know how to avoid this folder from being created, I have turn off the log in autogluon
rm -r AutogluonModels/

rm -r autogluon_models/*

python3 autogluon_model_predictor.py

rm -r AutogluonModels/

echo "training finished!"
#cd ..
#python3 -m predictor.model_training

