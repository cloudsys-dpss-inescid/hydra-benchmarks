## Cold start simulator

This is a small script that shows the impact that different cold starts can have on the execution time of various functions. It is based on the Azure dataset. Inside the script, you need to provide a path to the dataset in the `files_path` variable. The script will traverse the dataset and use the average execution duration, of each function, to calculate the impact of different cold starts, in percentage. The result of this script is a plot located in this folder. You can run the script like this: `./python3 avg_cost_simulator.py`.


