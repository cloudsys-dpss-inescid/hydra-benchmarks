import argparse
import matplotlib.pyplot as plt

file_path_template = 'results/decimals-{ndomains}.txt'

def get_decimals_list(path):
    decimals = []
    try:
        with open(path, 'r') as file:
            for line in file:
                decimals.append(float(line))
    except FileNotFoundError:
        print(f"The file at {path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return decimals

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--ndomains", type=int, required=True)
    args = parser.parse_args()
    fig, axes = plt.subplots(nrows=3, ncols=1)
    for i in range(2, 6):
        decimals = get_decimals_list(file_path_template.format(ndomains=i))
        axes[0].plot(list(range(1,len(decimals)+1)), decimals, label = f"{i} domains")
        axes[0].scatter(list(range(1,len(decimals)+1)), decimals)
        axes[0].set_title('Domain 2 to Domain 5')
    for i in range(6, 12):
        decimals = get_decimals_list(file_path_template.format(ndomains=i))
        axes[1].plot(list(range(1,len(decimals)+1)), decimals, label = f"{i} domains")
        axes[1].scatter(list(range(1,len(decimals)+1)), decimals)
        axes[1].set_title('Domain 6 to Domain 11')
    for i in range(12, args.ndomains + 1):
        decimals = get_decimals_list(file_path_template.format(ndomains=i))
        axes[2].plot(list(range(1,len(decimals)+1)), decimals, label = f"{i} domains")
        axes[2].scatter(list(range(1,len(decimals)+1)), decimals)
        axes[2].set_title('Domain 12 to Domain 15')

    #plt.tight_layout()
    # plt.ylabel("Time of Execution (us)")
    # plt.xlabel("No. of Invocations")
    # plt.title("Execution on Graal Native Image (Hello World)")
    plt.savefig(f'results/HelloWorld.png')

if __name__ == "__main__":
    main()