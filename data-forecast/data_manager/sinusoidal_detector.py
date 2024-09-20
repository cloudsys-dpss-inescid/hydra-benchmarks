import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.fft import fft, fftfreq
from scipy.optimize import curve_fit
import trace_generator

# This file was made to test if there was a way to detect whether a complete trace from Azure could be labeled as sinusoidal or not. 
# We want to use AutoGluon on sinusoidal traces and average on constant traces.
# I tested this on the most expensive traces in the dataset. There are some sinusoidal functions, but I did not succeed. 
# I used the standard deviation, assuming that if the std was larger, it would represent a more sinusoidal wave, but this approach did not work.
# I also tried using the Fourier transformation in two different ways to achieve the same goal, but both failed. However, this may still be the way forward, 
# as the generated plot from this file shows some promising heuristics in the middle column. These plots, located in complete_traces/traces_plots/ show that for more sinusoidal traces, 
# we observe fewer but higher peaks. The cosine function (injected into the dataset for testing purposes) shows the perfect scenario 
# and allows easy classification as sinusoidal.
# I also tried to find a similarity level between the tested trace and the perfect cosine wave, but the results were not great. 
# Additionally, I repeated all of this for each trace after applying a Gaussian filter, hoping it would improve accuracy, but it did not.


class TraceObj:
    
    def __init__(self, ID, dataframe, std, fft, cost_leaderboard_position, cost, gaussian_trace, gaussian_std, gaussian_fft, distance_of_max_values):
        self.ID = ID
        self.dataframe = dataframe
        self.std = std
        self.fft = fft
        self.cost_leaderboard_position = cost_leaderboard_position
        self.cost = cost
        # gaussian part
        self.gaussian_trace = gaussian_trace
        self.gaussian_std = gaussian_std
        self.gaussian_fft = gaussian_fft        
        self.distance_of_max_values = distance_of_max_values

# Define a sine wave function for fitting
def sine_wave(x, amplitude, frequency, phase, offset):
    return amplitude * np.sin(2 * np.pi * frequency * x + phase) + offset

# Function to calculate sine wave similarity using curve fitting
def sine_similarity_fft(df):
    # Convert timestamp to a numeric value (in seconds)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    x = (df['timestamp'] - df['timestamp'].min()).dt.total_seconds().values
    
    # Normalize x to avoid large numbers during fitting
    x_normalized = (x - x.min()) / (x.max() - x.min())
    
    # Extract values (y) and normalize them
    y = df['target'].values
    y = y - np.mean(y)  # Remove the offset
    
    # Guess initial parameters for the sine wave (amplitude, frequency, phase, offset)
    amplitude_guess = (y.max() - y.min()) / 2
    frequency_guess = 1 / (x_normalized.max() - x_normalized.min())  # Rough estimate
    phase_guess = 0
    offset_guess = np.mean(y)
    
    initial_guess = [amplitude_guess, frequency_guess, phase_guess, offset_guess]
    
    # Fit the sine wave to the data
    params, _ = curve_fit(sine_wave, x_normalized, y, p0=initial_guess)
    
    # Recreate the sine wave using the fitted parameters
    fitted_sine = sine_wave(x_normalized, *params)
    
    # Measure similarity (e.g., correlation coefficient)
    similarity = np.corrcoef(y, fitted_sine)[0, 1]
    
    return similarity, params

# this comes from Chat GPT when I asked to use the fourier transformation to identify a sinusoidal trace
def fftfreq_old(trace_target):
  
  #get standard deviation
  fft_values = np.fft.fft(trace_target)
  # Compute the Fourier Transform of the signal (target)
  frequencies = np.fft.fftfreq(len(trace_target))
  # Get the magnitude of the Fourier coefficients
  magnitudes = np.abs(fft_values)

  return frequencies, magnitudes

# https://stackoverflow.com/questions/73042887/python-how-i-can-draw-fft-graph-with-pandas-dataframe-which-is-made-by-time-an
def fftfreq_new(trace):
  
  t =  np.arange(0,len(trace['target']),1)
  s = trace['target']

  fft = np.fft.fft(s)
  fft[0] = 0
  fftfreq = np.fft.fftfreq(len(s))*len(s)/(t.max()-t.min())

  return fftfreq, fft


if __name__ == "__main__":
    dataset_dir = "../../azure-dataset/input/"
    complete_traces_dir = "data/complete_traces/"

    df = pd.read_csv('data/all_traces_cost.csv', sep=' ', header=None, names=['ID', 'Value'])
    df_sorted_desc = df.sort_values(by='Value', ascending=False)

    number_of_traces = 30 # get the 30 most expensive function from the trace
    ftt_cut = 40
    my_traces_dic = {}
    for idx, (index, row) in enumerate(df_sorted_desc.iterrows()):
      if idx >= number_of_traces:  
          break

      # get trace
      trace_id = row['ID']
      trace = trace_generator.read_csv_trace(trace_id, dataset_dir, complete_traces_dir)
      trace['timestamp'] = pd.to_datetime(trace['timestamp'])
      #get standard deviation
      std = trace["target"].std()
      # get fft for gausian, I do it to sort by fft, but the result was terrible
      _, magnitudes = fftfreq_old(trace['target'])

      # compute trace with gausian filter
      window_size = 5
      gaussian_trace = trace['target'].rolling(window=window_size).mean()
      # theres a problem on the first entrys after the rolling window
      for i in range(0, window_size):
          gaussian_trace[i] = trace['target'][i]     
      gaussian_trace = gaussian_filter(gaussian_trace, sigma=2)
      gaussian_std = gaussian_trace.std()
      # get fft for gausian, I do it to sort by fft, but the result was terrible
      _, gaussian_magnitudes = fftfreq_old(gaussian_trace)
      
      distance_of_max_values = sine_similarity_fft(trace)
      
      new_obj = TraceObj(trace_id, trace, round(std), round(np.max(magnitudes)), idx, round(row['Value']), gaussian_trace, round(gaussian_std), round(np.max(gaussian_magnitudes)), distance_of_max_values)
      my_traces_dic[trace_id] = new_obj

    # sort by some value of the object, if you want to change the parameter to sort, change to some other parameter of the TraceObj class. in this example, we are sorting fort distance_of_max_values. 
    # examples: std, fft, gaussian_std, gaussian_fft, distance_of_max_values
    file_name = "best_traces_sort_origina_distance_of_max_values"
    my_traces_dic = sorted(my_traces_dic.items(), key=lambda x:x[1].distance_of_max_values, reverse=True)
    my_traces_dic = dict(my_traces_dic)

    # Plot part
    mpl.rcParams["font.size"] = 25
    fig, axes = plt.subplots(nrows=number_of_traces, ncols=3, figsize=(40, 6 * number_of_traces))  # 3 columns: one for trace, the other two for fft frequencies

    for idx, trace_obj in enumerate(my_traces_dic.values()):
        if idx >= number_of_traces:
            break

        trace_id = trace_obj.ID
        trace = trace_obj.dataframe
        std = trace_obj.std
        fft = trace_obj.fft
        cost_leaderboard_position = trace_obj.cost_leaderboard_position
        cost = trace_obj.cost
        gaussian_trace = trace_obj.gaussian_trace
        gaussian_std = trace_obj.gaussian_std
        gaussian_fft = trace_obj.gaussian_fft    

        ###########
        # first plot
        ###########
        # Plotting the trace (time-series) on the first column
        ax1 = axes[idx, 0]

        ax1.plot(trace["timestamp"], trace["target"], label="original")        
        ax1.plot(trace["timestamp"], gaussian_trace, label="gaussian")

        ax1.legend()
        ax1.set_title(f"ID: {trace_id} Time-series \n cost_leaderboard: {cost_leaderboard_position}º, cost: {str(cost)}, std: {std}, fft: {fft}.\ngaussian, std: {gaussian_std}, fft: {gaussian_fft}.")
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Value')

        ###########
        ## second plot
        ###########
        # plot normal / original trace
        # Plotting the frequency spectrum (FFT) on the second column
        frequencies, magnitudes = fftfreq_old(trace['target'])

        ax2 = axes[idx, 1]
        ax2.plot(frequencies[:len(frequencies)//ftt_cut], magnitudes[:len(magnitudes)//ftt_cut], marker = '.', label="original")
        mean = magnitudes[:len(magnitudes)//ftt_cut].mean()
        ax2.axhline(y = mean, color = 'r', linestyle = '-', label =f" mean: {round(mean)}")

        # now plot with gausian filter
        frequencies, magnitudes = fftfreq_old(gaussian_trace)

        ax2.plot(frequencies[:len(frequencies)//ftt_cut], magnitudes[:len(magnitudes)//ftt_cut],  marker = '.', linestyle = '--', label="gaussian")
        
        ax2.legend()        
        ax2.set_xlabel('Frequency')
        ax2.set_ylabel('Magnitude')

        ###########
        ## third plot
        ###########

        fftfreq, fft = fftfreq_new(trace)
        ax3 = axes[idx, 2]
        ax3.plot(fftfreq, fft, marker = '.', label="original")
        ax3.legend()        
        ax3.set_xlabel('Frequency Domain')
        ax3.set_ylabel('Amplitude')

    plt.tight_layout()
    plt.savefig(f"data/complete_traces/traces_plots/{file_name}.png", bbox_inches='tight')
    plt.close()
