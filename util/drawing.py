import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def draw_waterfall(filename):
    plt.clf()
    np.random.seed(19680801)

    dt = 0.0005
    t = np.arange(0.0, 20.0, dt)
    s1 = np.sin(2 * np.pi * 100 * t)
    s2 = 2 * np.sin(2 * np.pi * 400 * t)

    # create a transient "chirp"
    s2[t <= 10] = s2[12 <= t] = 0

    # add some noise into the mix
    nse = 0.01 * np.random.random(size=len(t))

    x = s1 + s2 + nse  # the signal
    NFFT = 1024  # the length of the windowing segments
    Fs = int(1.0 / dt)  # the sampling frequency

    fig, (ax1) = plt.subplots(nrows=1)
    # ax1.plot(t, x)
    Pxx, freqs, bins, im = ax1.specgram(x, NFFT=NFFT, Fs=Fs, noverlap=900)
    # The `specgram` method returns 4 objects. They are:
    # - Pxx: the periodogram
    # - freqs: the frequency vector
    # - bins: the centers of the time bins
    # - im: the matplotlib.image.AxesImage instance representing the data in the plot
    fig.savefig(filename)


def draw_a_serias(filename, points=[], peaks=[], shapes=[], skewness=[]):
    plt.clf()
    # need to adjust linux(centos)
    chinese =matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')
    # ax1 = plt.axes()
    if len(points) == 0: 
        # draw example
        points = list(range(34,44,1))
        peaks = np.sin(points)
        skewness = np.cos(points)
        shapes = np.tan(points)
    line1, = plt.plot(points, shapes, 'r', label="line 1")
    # plt.show()
    line2, = plt.plot(points, skewness, 'g', label="line 2")
    line3, = plt.plot(points, peaks, 'b', label="line 3")
    # plt.legend((line1, line2, line3), ('label1', 'label2', 'label3'))
    plt.legend([line3, line1, line2], [u'峰值系数', u'形状参数', u'偏度系数'], prop=chinese)
    plt.savefig(filename)

def draw_b_serias(filename, points=[], entropy=[], zerocross=[]):
    plt.clf()
    # need to adjust linux(centos)
    chinese =matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')
    # ax1 = plt.axes()
    if len(points) == 0: 
        # draw example
        points = list(range(34,44,1))
        entropy = np.sin(points)
        zerocross = np.cos(points)
        # shapes = np.tan(points)
    line1, = plt.plot(points, entropy, 'r', label="line 1")
    # plt.show()
    line2, = plt.plot(points, zerocross, "tab:orange", label="line 2")
    # plt.legend((line1, line2, line3), ('label1', 'label2', 'label3'))
    plt.legend([line1, line2], [u'信息熵', u'过零率'], prop=chinese)
    plt.savefig(filename)

def draw_fluctuation(filename, points=[], fluctuation=[]):
    plt.clf()
    # need to adjust linux(centos)
    chinese =matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')
    # ax1 = plt.axes()
    if len(points) == 0: 
        # draw example
        points = list(range(34,44,1))
        fluctuation = np.sin(points)
    line1, = plt.plot(points, fluctuation, 'b', label="line 1")
    # plt.show()
    # plt.legend((line1, line2, line3), ('label1', 'label2', 'label3'))
    plt.legend([line1], [u'方差'], prop=chinese)
    plt.savefig(filename)

def draw_freq(filename, points=[], freq=[]):
    plt.clf()
    # need to adjust linux(centos)
    chinese =matplotlib.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')
    # ax1 = plt.axes()
    if len(points) == 0: 
        # draw example
        points = list(range(34,44,1))
        freq = np.sin(points)
    line1, = plt.plot(points, freq, 'b', label="line 1")
    plt.legend([line1], [u'频率'], prop=chinese)
    plt.savefig(filename)



if __name__ == '__main__':
    draw_a_serias("./test.png")