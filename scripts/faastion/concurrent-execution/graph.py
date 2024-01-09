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

    for i in range(2, args.ndomains + 1):
        decimals = get_decimals_list(file_path_template.format(ndomains=i))
        
        plt.plot(list(range(1,len(decimals)+1)), decimals, label = f"{i} domains")
        plt.scatter(list(range(1,len(decimals)+1)), decimals)

    plt.legend()
    plt.ylabel("Time of Execution (us)")
    plt.xlabel("No. of Invocations")
    plt.title("Execution on Graal Native Image (Hello World)")
    plt.savefig(f'results/HelloWorld.png')

if __name__ == "__main__":
    main()