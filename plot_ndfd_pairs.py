import os, argparse, sys

import numpy as np
import sparse
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

plt.rc('font', family='serif')

def main(INPUT_DIR, N, NSKIP, NICE_PLOT, OVERLAY, FD_DIR, ND_DEPO_DIR, DOWNRES):
    diffs = []
    for i, entry in enumerate(os.scandir(INPUT_DIR)):
        if i < NSKIP:
            continue
        if N and i >= N + NSKIP:
            break
        if not (entry.name.endswith('.npy') or entry.name.endswith('.npz')):
            continue

        print(entry.name, end='\r')
        if FD_DIR:
            arr_nd = np.load(entry.path) if entry.name.endswith('.npy') else sparse.load_npz(entry.path).todense()
            arr_nd = arr_nd[0, :, :]

            num = int(entry.name[:-6])
            arr_fd = np.load(os.path.join(FD_DIR, '{}fd.npy'.format(num)))
            arr_fd = arr_fd[0, :, :]

        else:
            arr_ndfd = np.load(entry.path)
            arr_nd = arr_ndfd[0, :, :4608]
            arr_fd = arr_ndfd[0, :, 4608:]

        if ND_DEPO_DIR:
            num = int(entry.name[:-6])
            arr_depo = np.load(os.path.join(ND_DEPO_DIR, '{}depo.npy'.format(num)))
            arr_depo = arr_depo[0, :, :]

        if arr_nd.shape[0] == 512:
            arr_nd = arr_nd[16:-16, 58:-58]
            arr_fd = arr_fd[16:-16, 58:-58]
            cmap = 'viridis'
            vmin, vmax = np.min(arr_fd), np.max(arr_fd)
            if ND_DEPO_DIR:
                arr_depo = arr_depo[16:-16, 58:-58]

        elif arr_nd.shape[0] == 480:
            cmap = 'viridis'
            vmin, vmax = np.min(arr_fd), np.max(arr_fd)
            if ND_DEPO_DIR:
                arr_depo = arr_depo
            
        elif arr_nd.shape[0] == 1024:
            arr_nd = arr_nd[112:-112, 58:-58]
            arr_fd = arr_fd[112:-112, 58:-58]
            cmap = 'seismic'
            fd_abs_max = np.max(np.abs(arr_fd))
            vmin, vmax = -fd_abs_max, fd_abs_max
            if ND_DEPO_DIR:
                arr_depo = arr_depo[112:-112, 58:-58]

        elif arr_nd.shape[0] == 800:
            cmap = 'seismic'
            fd_abs_max = np.max(np.abs(arr_fd))
            vmin, vmax = -fd_abs_max, fd_abs_max
            if ND_DEPO_DIR:
                arr_depo = arr_depo

        if OVERLAY:
            # Cropping
            non_zeros = np.nonzero(arr_nd)
            ch_min = non_zeros[0].min() - 10 if (non_zeros[0].min() - 10) > 0 else 0
            ch_max = non_zeros[0].max() + 11 if (non_zeros[0].max() + 11) < 480 else 480
            tick_min = non_zeros[1].min() - 50 if (non_zeros[1].min() - 50) > 0 else 0
            tick_max = non_zeros[1].max() + 51 if (non_zeros[1].max() + 51) < 4492 else 4492
            arr_nd = arr_nd[ch_min:ch_max, tick_min:tick_max]
            arr_fd = arr_fd[ch_min:ch_max, tick_min:tick_max]

            fig, ax = plt.subplots(1, 1, figsize=(12, 12), tight_layout=True)

            arr_nd[arr_nd != 0] = 100

            ax.imshow(arr_fd.T, cmap='coolwarm', aspect='auto', interpolation='none', origin='lower', alpha=0.6, vmin=-100, vmax=100)
            ax.imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='Blues', aspect='auto', interpolation='none', origin='lower', vmin=0, vmax=100)
         
            plt.show()

            continue

        if NICE_PLOT: # Plot for presentations
            if entry.name not in ['1ndfd.npy', '14ndfd.npy']:
                continue

            if entry.name == '1ndfd.npy':
                pdf = PdfPages('1ndfd_evd.pdf')

                arr_nd = np.roll(arr_nd, 52, 1)
                arr_nd = arr_nd + np.roll(arr_nd, -1 ,1)

                fig, ax = plt.subplots(1, 2, figsize=(16, 6), tight_layout=True)

                ax[0].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower', vmin=0)
                ax[0].set_title("ND", fontsize=16)
                ax[0].set_xlabel("FD Wire", fontsize=14)
                ax[0].set_ylabel("Tick [0.5us]", fontsize=14)
                ax[0].set_xlim(60, 240)
                ax[0].set_ylim(620, 2000)
                ax[0].set_yticklabels([])
                ax[0].set_xticklabels([])
                ax[0].set_xticks([])
                ax[0].set_yticks([]) 

                ax[1].imshow(arr_fd.T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
                ax[1].set_title("FD", fontsize=14)
                ax[1].set_xlabel("FD Wire", fontsize=14)
                ax[1].set_xlim(60, 240)
                ax[1].set_ylim(620, 2000)
                ax[1].set_yticklabels([])
                ax[1].set_xticklabels([])
                ax[1].set_xticks([])
                ax[1].set_yticks([]) 

                pdf.savefig(bbox_inches='tight')
                pdf.close()
                plt.close()

                continue

            if entry.name == '14ndfd.npy':
                pdf = PdfPages('14ndfd_trace.pdf')

                arr_nd = np.roll(arr_nd, 52, 1)

                ch = (0, 0)
                for i, col in enumerate(arr_nd):
                    if np.abs(col).sum() > ch[1]:
                        ch = (i, np.abs(col).sum())
                ch = ch[0]

                ticks_nd = arr_nd[ch, :]
                ticks_fd = arr_fd[ch, :]
                ticks = np.arange(1, arr_nd.shape[1] + 1)

                fig, ax = plt.subplots(figsize=(16, 4),tight_layout=True)

                ax.hist(ticks, bins=len(ticks), weights=ticks_nd, histtype='step', linewidth=0.7, color='b', label='ND')
                ax.hist(ticks, bins=len(ticks), weights=ticks_fd, histtype='step', linewidth=0.7, color='r', label='FD')
                ax.set_xlim(600, 900)
                ax.set_ylabel("ADC", fontsize=14)
                ax.set_xlabel("tick", fontsize=14)

                handles, labels = ax.get_legend_handles_labels()
                new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
                plt.legend(handles=new_handles, labels=labels, prop={'size': 12})

                pdf.savefig(bbox_inches='tight')
                pdf.close()
                plt.close()

                continue

        if DOWNRES:
            # arr_nd_smear = arr_nd.copy()
            # for i in range(5):
            #     arr_nd_smear += np.roll(arr_nd_smear, i + 1, 1)  

            fig, ax = plt.subplots(1, 2, figsize=(16, 6), tight_layout=True)

            if 'Z' in entry.path.split('/')[-2]:
                cmap = 'viridis'
                vmin = arr_fd.min()
                vmax = arr_fd.max()
            elif ('U' in entry.path.split('/')[-2]) or ('V' in entry.path.split('/')[-2]):
                cmap = 'seismic'
                vmin = -np.abs(arr_fd).max()
                vmax = np.abs(arr_fd).max()
        
            ax[0].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', interpolation='none', aspect='auto', origin='lower')
            ax[1].imshow(arr_fd.T, cmap=cmap, interpolation='none', aspect='auto', origin='lower', vmin=vmin, vmax=vmax)

            plt.show()

            # Assumming (8,8) upresolution
            arr_nd_downres = np.zeros((int(arr_nd.shape[0]/8), int(arr_nd.shape[1]/8)))
            for ch, ch_vec in enumerate(arr_nd): 
                for tick, adc in enumerate(ch_vec): 
                    arr_nd_downres[int(ch/8), int(tick/8)] += adc 
            arr_nd = arr_nd_downres 

            ch = (0, 0)
            for idx, col in enumerate(arr_nd):
                if np.abs(col).sum() > ch[1]:
                    ch = (idx, np.abs(col).sum())
            ch = ch[0]

            tick_adc_fd = arr_fd[ch, :]
            tick_adc_nd = arr_nd[ch, :]
            ticks = np.arange(1, arr_nd.shape[1] + 1)

            fig, ax = plt.subplots()

            ax.hist(ticks, bins=len(ticks), weights=tick_adc_nd, histtype='step', label='ND', linewidth=0.8, color='g')
            ax.set_ylabel("ND ADC", fontsize=14)
            ax.set_xlabel("tick", fontsize=14)
            
            ax2 = ax.twinx()
            ax2.hist(ticks, bins=len(ticks), weights=tick_adc_fd, histtype='step', label='FD', linewidth=0.8, color='r')
            ax2.set_ylabel("FD ADC", fontsize=14)

            ax_ylims = ax.axes.get_ylim()
            ax_yratio = ax_ylims[0] / ax_ylims[1]
            ax2_ylims = ax2.axes.get_ylim()
            ax2_yratio = ax2_ylims[0] / ax2_ylims[1]
            if ax_yratio < ax2_yratio:
                ax2.set_ylim(bottom=ax2_ylims[1]*ax_yratio)
            else:
                ax.set_ylim(bottom=ax_ylims[1]*ax2_yratio)
            
            handles, labels = ax.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles += handles2
            labels += labels2
            new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
            plt.legend(handles=new_handles, labels=labels, prop={'size' : 14})
            
            fig.tight_layout()
            plt.show()

            continue

        # Looking at tick shift (coming from somewhere inside WireCell that can de accessed in LArSoft so stuck with for now)
        # for i, (row_nd, row_fd) in enumerate(zip(arr_nd, arr_fd)):
        #       if row_nd.sum() > 100:
        #           if (np.max(np.argwhere(row_nd > 0)) - np.min(np.argwhere(row_nd > 0))) > 10:
        #               continue
        #           if np.abs(np.argmax(row_fd) - np.argmax(row_nd)) > 100:
        #               continue
        #           if np.abs(np.argmax(row_fd) - np.argmax(row_nd)) < 0:
        #               continue
        #           diffs.append(np.argmax(row_fd) - np.argmax(row_nd))
        # # if entry.name != "20ndfd.npy":
        # #     continue
        # continue

        # Manipulate array
        # arr_fd = np.flip(arr_fd, 1)
        # # arr_nd = np.roll(arr_nd, 52, 1)
        # arr_nd_newres = np.zeros((480, 8984))
        # for i_ch, col in enumerate(arr_nd):
        #       for i_tick, adc in enumerate(col):
        #           if adc != 0:
        #               # arr_nd_newres[i_ch, int(2*i_tick) - 4:int(2*i_tick)] += adc
        #               arr_nd_newres[i_ch, int(2*i_tick)] = adc
        # # for i_tick, row in enumerate(arr_nd_newres.T):
        # #     if arr_nd_newres[:, i_tick].sum() != 0: 
        # #         print('\n')
        # #         print(i_tick)
        # #         break
        # arr_nd = arr_nd_newres[:, 3251:3251 + 4492]

        if ND_DEPO_DIR:
            fig, ax = plt.subplots(1, 3)

            ax[0].imshow(np.ma.masked_where(arr_depo == 0, arr_depo).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
            ax[0].set_title("Depos")

            ax[1].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
            ax[1].set_title("ND")

            ax[2].imshow(arr_fd.T, cmap=cmap, aspect='auto', interpolation='none', origin='lower', vmin=vmin, vmax=vmax)
            ax[2].set_title("FD")

            fig.tight_layout()
            plt.show()

            ch = (0, 0)
            for i, col in enumerate(arr_nd):
                if np.abs(col).sum() > ch[1]:
                    ch = (i, np.abs(col).sum())
            ch = ch[0]

            ticks_nd = arr_nd[ch, :]
            ticks_fd = arr_fd[ch, :]
            ticks_depo = arr_depo[ch, :]
            ticks = np.arange(1, arr_nd.shape[1] + 1)

            fig, ax = plt.subplots(tight_layout=True)

            ax.hist(ticks, bins=len(ticks), weights=ticks_nd, histtype='step', linewidth=0.7, color='b', label='ND')
            ax.hist(ticks, bins=len(ticks), weights=ticks_fd, histtype='step', linewidth=0.7, color='r', label='FD')
            ax.set_ylabel("ADC", fontsize=14)
            ax.set_xlabel("tick", fontsize=14)

            ax2 = ax.twinx()
            ax2.hist(ticks, bins=len(ticks), weights=ticks_depo, histtype='step', linewidth=0.7, color='g', label='Depos')
            ax2.set_ylabel("electrons")
    
            ax_ylims = ax.axes.get_ylim()
            ax_yratio = ax_ylims[0] / ax_ylims[1]
            ax2_ylims = ax2.axes.get_ylim()
            ax2_yratio = ax2_ylims[0] / ax2_ylims[1]
            if ax_yratio < ax2_yratio:
                ax2.set_ylim(bottom=ax2_ylims[1]*ax_yratio)
            else:
                ax.set_ylim(bottom=ax_ylims[1]*ax2_yratio)

            plt.title("Channel {} in ROP".format(ch), fontsize=16)

            handles, labels = ax.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            handles += handles2
            labels += labels2
            new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
            plt.legend(handles=new_handles, labels=labels, prop={'size': 12})

            plt.show()

            continue

        fig, ax = plt.subplots(1, 2)

        ax[0].imshow(np.ma.masked_where(arr_nd == 0, arr_nd).T, cmap='viridis', aspect='auto', interpolation='none', origin='lower')
        ax[0].set_title("ND")

        ax[1].imshow(arr_fd.T, cmap=cmap, aspect='auto', interpolation='none', origin='lower', vmin=vmin, vmax=vmax)
        ax[1].set_title("FD")

        fig.tight_layout()
        plt.show()

        ch = (0, 0)
        for i, col in enumerate(arr_nd):
            if np.abs(col).sum() > ch[1]:
                ch = (i, np.abs(col).sum())
        ch = ch[0]

        ticks_nd = arr_nd[ch, :]
        ticks_fd = arr_fd[ch, :]
        ticks = np.arange(1, arr_nd.shape[1] + 1)

        fig, ax = plt.subplots(tight_layout=True)

        ax.hist(ticks, bins=len(ticks), weights=ticks_nd, histtype='step', linewidth=0.7, color='b', label='ND')
        ax.hist(ticks, bins=len(ticks), weights=ticks_fd, histtype='step', linewidth=0.7, color='r', label='FD')
        ax.set_ylabel("ADC", fontsize=14)
        ax.set_xlabel("tick", fontsize=14)

        plt.title("Channel {} in ROP".format(ch), fontsize=16)

        handles, labels = ax.get_legend_handles_labels()
        new_handles = [Line2D([], [], c=h.get_edgecolor()) for h in handles]
        plt.legend(handles=new_handles, labels=labels, prop={'size': 12})

        plt.show()

    # Looking at tick shift  
    # print(diffs)
    # print("{} +- {}".format(np.mean(diffs), np.std(diffs)))

def parse_arguments():
        parser = argparse.ArgumentParser()

        parser.add_argument("input_dir")

        parser.add_argument("-n", type=int, default=0, dest='n')
        parser.add_argument("--nskip", type=int, default=0)
        parser.add_argument("--nice_plot", action='store_true')
        parser.add_argument("--overlay", action='store_true')
        parser.add_argument("--separate_fd_dir", type=str, default='')
        parser.add_argument("--nd_depo_dir", type=str, default='')
        parser.add_argument("--downres", action='store_true')

        # group1 = parser.add_mutually_exclusive_group()
        # group1.add_argument("--induction", action='store_true')
        # group1.add_argument("--collection", action='store_true')

        args = parser.parse_args()

        return (args.input_dir, args.n, args.nskip, args.nice_plot, args.overlay, args.separate_fd_dir, args.nd_depo_dir, args.downres)

if __name__ == "__main__":
        arguments = parse_arguments()
        main(*arguments)

