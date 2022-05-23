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
