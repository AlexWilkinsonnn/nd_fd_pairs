import os, argparse

import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm
import ROOT, sparse

def get_packets(nd_projections_root, eventid):
    f = ROOT.TFile.Open(nd_projections_root, "READ")
    t = f.Get("IonAndScint/packet_projections")

    nd_packets = { 'x' : [], 'y' : [], 'z': [], 'adc' : [] }
    nd_packets_projection = { 'Z' : [], 'U' : [], 'V' : [] }

    for event in t:
        if event.eventid == eventid:
            for hit in event.projection:
                x = hit[0] # beam direction
                y = hit[1]
                z = hit[2] # drift direction
                chZ = int(hit[3])
                tickZ = int(hit[4])
                chU = int(hit[5])
                tickU = int(hit[6])
                chV = int(hit[7])
                chV = chV - 200 if chV - 200 > 0 else 600 + chV
                tickV = int(hit[8])
                adc = int(hit[9])

                nd_packets['x'].append(x)
                nd_packets['y'].append(y)
                nd_packets['z'].append(z)
                nd_packets['adc'].append(adc)

                nd_packets_projection['Z'].append((chZ, tickZ, adc))
                nd_packets_projection['U'].append((chU, tickU, adc))
                nd_packets_projection['V'].append((chV, tickV, adc))

            break

    return nd_packets, nd_packets_projection

def crop_nd_fd(nd, fd):
    non_zeros = np.nonzero(nd)

    ch_min = non_zeros[0].min() - 10 if (non_zeros[0].min() - 10) > 0 else 0
    ch_max = non_zeros[0].max() + 11 if (non_zeros[0].max() + 11) < nd.shape[0] else nd.shape[0] 
    tick_min = non_zeros[1].min() - 50 if (non_zeros[1].min() - 50) > 0 else 0
    tick_max = non_zeros[1].max() + 51 if (non_zeros[1].max() + 51) < 4492 else 4492 

    nd = nd[ch_min:ch_max, tick_min:tick_max]
    fd = fd[ch_min:ch_max, tick_min:tick_max]

    return nd, fd

def main(ND_PROJECTIONS, EVENTID, FD_Z, FD_U, FD_V, OUT_DIR, SHOW_ONLY):
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    nd_packets, nd_packets_projection = get_packets(ND_PROJECTIONS, EVENTID)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.scatter(nd_packets['x'], nd_packets['x'], nd_packets['z'], c=nd_packets['adc'], marker='s', cmap='jet', s=3)
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])
    ax.zaxis.set_ticklabels([])
    if SHOW_ONLY:
        plt.show()
    else:
        plt.savefig(os.path.join(OUT_DIR, "nd_packets.pdf"), bbox_inches='tight')
    
    nd_Z = np.zeros((480, 4492))
    for ch, tick, adc in nd_packets_projection['Z']:
        nd_Z[ch, tick-2:tick+3] += adc
    nd_U = np.zeros((800, 4492))
    for ch, tick, adc in nd_packets_projection['U']:
        nd_U[ch, tick-2:tick+3] += adc
    nd_V = np.zeros((800, 4492))
    for ch, tick, adc in nd_packets_projection['V']:
        nd_V[ch, tick-2:tick+3] += adc

    fd_Z = np.load(FD_Z)[0, 16:-16, 58:-58]
    fd_U = np.load(FD_U)[0, 112:-112, 58:-58]
    fd_V = np.roll(np.load(FD_V)[0, 112:-112, 58:-58], -200, 0)

    # nd_Z, fd_Z = crop_nd_fd(nd_Z, fd_Z)
    # nd_U, fd_U = crop_nd_fd(nd_U, fd_U)
    # nd_V, fd_V = crop_nd_fd(nd_V, fd_V)

    # hardcoded cropping for eventid 6
    nd_Z = nd_Z[50:350, 1650:2550]
    fd_Z = fd_Z[50:350, 1650:2550]
    nd_U = nd_U[500:800, 1650:2550]
    fd_U = fd_U[500:800, 1650:2550]
    nd_V = nd_V[380:680, 1650:2550]
    fd_V = fd_V[380:680, 1650:2550]

    if SHOW_ONLY:
        fig, ax = plt.subplots(1, 3)
        ax[0].imshow(np.ma.masked_where(nd_Z == 0, nd_Z).T, interpolation='none', origin='lower', cmap='viridis', aspect=(1/3))
        ax[1].imshow(np.ma.masked_where(nd_U == 0, nd_U).T, interpolation='none', origin='lower', cmap='viridis', aspect=(1/3))
        ax[2].imshow(np.ma.masked_where(nd_V == 0, nd_V).T, interpolation='none', origin='lower', cmap='viridis', aspect=(1/3))
        fig.tight_layout()
        plt.show()
        
        fig, ax = plt.subplots(1, 3)
        ax[0].imshow(fd_Z.T, interpolation='none', origin='lower', cmap='viridis')
        ax[1].imshow(fd_U.T, interpolation='none', origin='lower', cmap='seismic', vmin=-np.abs(fd_U).max(), vmax=np.abs(fd_U).max())
        ax[2].imshow(fd_V.T, interpolation='none', origin='lower', cmap='seismic', vmin=-np.abs(fd_V).max(), vmax=np.abs(fd_V.max()))
        fig.tight_layout()
        plt.show()

    else:
        for name, nd_im in zip(["nd_Z", "nd_U", "nd_V"], [nd_Z, nd_U, nd_V]):
            fig, ax = plt.subplots(1, 1)

            ax.imshow(np.ma.masked_where(nd_im == 0, nd_im).T, interpolation='none', origin='lower', cmap='viridis', aspect=(1/3))
            ax.set_axis_off()

            fig.tight_layout()
            plt.savefig(os.path.join(OUT_DIR, name + ".pdf"), bbox_inches='tight')

        fig, ax = plt.subplots(1, 1)

        ax.imshow(fd_Z.T, interpolation='none', origin='lower', cmap='viridis', aspect=(1/3))
        ax.set_axis_off()

        fig.tight_layout()
        plt.savefig(os.path.join(OUT_DIR, "fd_Z.pdf"), bbox_inches='tight')
        
        for name, fd_im in zip(["fd_U", "fd_V"], [fd_U, fd_V]):
            fig, ax = plt.subplots(1, 1)

            ax.imshow(fd_im.T, interpolation='none', origin='lower', cmap='seismic', aspect=(1/3), vmin=-np.abs(fd_im).max(), vmax = np.abs(fd_im).max())
            ax.set_axis_off()

            fig.tight_layout()
            plt.savefig(os.path.join(OUT_DIR, name + ".pdf"), bbox_inches='tight')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Plots to make a flow chart of the ND->FD translation, hardcoded for eventid 6")

    parser.add_argument("nd_projections", type=str)
    parser.add_argument("eventid", type=int)
    parser.add_argument("fd_Z", type=str)
    parser.add_argument("fd_U", type=str)
    parser.add_argument("fd_V", type=str)
    parser.add_argument("out_dir", type=str)

    parser.add_argument("--show_only", action='store_true')

    args = parser.parse_args()

    return (args.nd_projections, args.eventid, args.fd_Z, args.fd_U, args.fd_V, args.out_dir, args.show_only)

if __name__ == "__main__":
    arguments = parse_arguments()
    main(*arguments)

