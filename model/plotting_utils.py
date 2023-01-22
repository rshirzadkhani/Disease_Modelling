import matplotlib.pyplot as plt

def plot_for_contact_network(x, sir_all,ci, filename, labels):
    colors = ["#8B2323" ,"#fe9929","#67a9cf","#2E2E2E"]
    lnstyle = ['solid','dashed','dashed', 'solid']
    fig = plt.figure(facecolor='w', figsize=(9,7))
    ax = fig.add_subplot(111)
    for idx, label in enumerate(labels):
        ax.plot(x, sir_all[idx, :], color=colors[idx % len(colors)], linestyle = lnstyle[idx], lw=3.5, label=label)
        ax.fill_between(x, (sir_all[idx, :]-ci[idx, :]), (sir_all[idx, :]+ci[idx, :]), color=colors[idx % len(colors)], alpha=.15)
    
    ax.set_xlabel("Time", fontsize=31)
    ax.set_ylabel('Infections', fontsize=31)
    ax.tick_params(labelsize=35)
    ax.grid(b=False)
    legend = ax.legend(fontsize=26)
    legend.get_frame().set_alpha(0.95)
    plt.tight_layout()
    plt.show()
    plt.savefig(filename)