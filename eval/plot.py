import matplotlib.pyplot as plt
from matplotlib.ticker import (AutoMinorLocator)


def boxplot(data, filename, xticks=None, title='', yticks=None, ylimits=None, yscale='linear', xaxis_label="",
            yaxis_label=""):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.boxplot(data,
               boxprops=dict(linewidth=4, color='blue'),
               medianprops=dict(linewidth=4, color='red'),
               whiskerprops=dict(linewidth=4, color='black'),
               capprops=dict(linewidth=4),
               whis=[1, 99])

    if xticks is not None:
        plt.xticks(list(range(1, len(xticks) + 1)), xticks)

    if yticks is not None:
        plt.yticks(yticks)
    if ylimits is not None:
        ax.set_ylim(ylimits)

    plt.yscale(yscale)

    ax.tick_params(axis='x', rotation=0, labelsize=20)
    ax.tick_params(axis='y', rotation=0, labelsize=20)

    ax.set_xlabel(xaxis_label, fontsize=20)
    ax.set_ylabel(yaxis_label, fontsize=20)

    # grid
    plt.grid(True, color='lightgray', which='both', axis='y', linestyle='-')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)

    plt.tight_layout()  # improve margins for example for yaxis_label

    # plt.show()
    fig.savefig(filename)
    print(f'plot {filename} created')


def histogram(data, filename, title='', xaxis_label="", yaxis_label="", yscale='linear'):
    fig, ax = plt.subplots()
    ax.set_title(title)
    ax.hist(data,
            bins=100,
            density=False)

    plt.yscale(yscale)

    ax.tick_params(axis='x', rotation=0, labelsize=20)
    ax.tick_params(axis='y', rotation=0, labelsize=20)

    ax.set_ylabel(yaxis_label, fontsize=20)
    ax.set_xlabel(xaxis_label, fontsize=20)

    # grid
    plt.grid(True, color='lightgray', which='both', axis='y', linestyle='-')
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(which='both', width=2)
    ax.tick_params(which='major', length=7)

    plt.tight_layout()  # improve margins for example for yaxis_label

    # plt.show()
    fig.savefig(filename)
    print(f'plot {filename} created')

def draw_points(
        results,
        filename,
        xaxis_label="",
        yaxis_label="",
        convert=False):
    """Draw given results as points."""

    # Convert list of results.
    if convert:
        results = list(zip(*results))

    # Size parameters:
    plt.rcParams.update({'font.size': 17})
    plt.rcParams.update({'figure.subplot.top': 0.99})
    plt.rcParams.update({'figure.subplot.bottom': 0.25})
    plt.rcParams.update({'figure.subplot.left': 0.18})
    plt.rcParams.update({'figure.subplot.right': 0.99})
    plt.rcParams.update({'figure.figsize': [7, 4.8]})

    # Draw plots:
    fig1, ax1 = plt.subplots()

    total_max = max(results[0] + results[1])
    total_min = min(results[0] + results[1])
    ax1.set_ylim([total_min,total_max])
    ax1.set_xlim([total_min,total_max])
    ax1.set_yscale('log')
    ax1.set_xscale('log')

    plt.plot(results[0], results[1], 'o')

     # horizontal line
    ax1.plot([0, 1], [0, 1], '--', transform=ax1.transAxes)

    ax1.set_xlabel(xaxis_label, fontsize=22)
    ax1.set_ylabel(yaxis_label, fontsize=22)
    plt.tight_layout()

    # Save.
    plt.savefig(filename)
