"""
Helper class to track length of time taken for each frame and draw a graph when application exits.
Also able to add events at arbitrary times across the graph.
"""
import time
import matplotlib.pyplot as plt
import statistics

class FrametimePlotter:
    EVENT_POINT_Y = -0.05
    EVENT_MSG_Y = -0.045

    def __init__(self):
        self.times = []
        self.events = []
        self.start = time.perf_counter()

    def add_event(self, event_msg):
        self.events.append( (len(self.times), event_msg))

    def end_frame(self, time_delta):
        self.times.append(time_delta)

    def _show_stats(self):
        end = time.perf_counter()
        print("Min   : {:.5f}".format(min(self.times)))
        print("Max   : {:.5f}".format(max(self.times)))
        print("Avg   : {:.5f}".format(statistics.mean(self.times)))
        print("Median: {:.5f}".format(statistics.median(self.times)))
        try:
            print("Mode  : {:.5f}".format(statistics.mode(self.times)))
        except statistics.StatisticsError as e:
            print("Mode  : {}".format(e))
        print("StdDev: {:.5f}".format(statistics.stdev(self.times)))
        frame_count = len(self.times)
        elapsed_time = end - self.start
        print("Frame count: {}".format(frame_count))
        print("Elapsed time: {:.5f}".format(elapsed_time))
        print("FPS: {:.5f}".format(frame_count / elapsed_time))

    def show(self):
        if len(self.times) <= 1:
            return
        self._show_stats()
        frame_idxs = range(0, len(self.times))
        event_idxs = [e[0] for e in self.events]
        event_point_y = [self.EVENT_POINT_Y] * len(self.events)
        plt.figure("Frame durations", figsize=(8, 6))
        plt.plot(frame_idxs, self.times, event_idxs, event_point_y, "k|")
        plt.xlabel("frames")
        plt.ylabel("frame duration")
        plt.ylim(self.EVENT_POINT_Y-0.005, 0.5)
        plt.tight_layout()
        for frame_idx, msg in self.events:
            plt.text(frame_idx, self.EVENT_MSG_Y, msg, horizontalalignment="center", verticalalignment="bottom", size="smaller", rotation="vertical")
        plt.show()
