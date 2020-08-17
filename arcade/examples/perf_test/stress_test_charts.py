import csv
import matplotlib.pyplot as plt

SPRITE_COUNT = 1
PROCESSING_TIME = 3
DRAWING_TIME = 4


def read_results(filename):
    results = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            results.append([float(cell) for cell in row])
        return results


def chart_stress_test_draw_moving_pygame():
    results = read_results("stress_test_draw_moving_pygame.csv")

    sprite_count = [row[SPRITE_COUNT] for row in results]
    processing_time = [row[PROCESSING_TIME] for row in results]
    drawing_time = [row[DRAWING_TIME] for row in results]

    # Plot our results
    plt.title("Moving and Drawing Sprites In Pygame")
    plt.plot(sprite_count, processing_time, label="Processing Time")
    plt.plot(sprite_count, drawing_time, label="Drawing Time")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    plt.savefig("chart_stress_test_draw_moving_pygame.svg")
    # plt.show()
    plt.clf()


def chart_stress_test_draw_moving_arcade():
    results = read_results("stress_test_draw_moving_arcade.csv")

    sprite_count = [row[SPRITE_COUNT] for row in results]
    processing_time = [row[PROCESSING_TIME] for row in results]
    drawing_time = [row[DRAWING_TIME] for row in results]

    # Plot our results
    plt.title("Moving and Drawing Sprites In Arcade")
    plt.plot(sprite_count, processing_time, label="Processing Time")
    plt.plot(sprite_count, drawing_time, label="Drawing Time")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    # plt.show()
    plt.savefig("chart_stress_test_draw_moving_arcade.svg")
    plt.clf()


def chart_stress_test_draw_moving_draw_comparison():
    r1 = read_results("stress_test_draw_moving_arcade.csv")
    r2 = read_results("stress_test_draw_moving_pygame.csv")

    sprite_count = [row[SPRITE_COUNT] for row in r1]
    d1 = [row[DRAWING_TIME] for row in r1]
    d2 = [row[DRAWING_TIME] for row in r2]

    # Plot our results
    plt.title("Drawing Sprites - Arcade vs. Pygame")
    plt.plot(sprite_count, d1, label="Drawing Time Arcade")
    plt.plot(sprite_count, d2, label="Drawing Time Pygame")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    # plt.show()
    plt.savefig("chart_stress_test_draw_moving_draw_comparison.svg")
    plt.clf()


def chart_stress_test_draw_moving_process_comparison():
    r1 = read_results("stress_test_draw_moving_arcade.csv")
    r2 = read_results("stress_test_draw_moving_pygame.csv")

    sprite_count = [row[SPRITE_COUNT] for row in r1]
    d1 = [row[PROCESSING_TIME] for row in r1]
    d2 = [row[PROCESSING_TIME] for row in r2]

    # Plot our results
    plt.title("Moving Sprites - Arcade vs. Pygame")
    plt.plot(sprite_count, d1, label="Processing Time Arcade")
    plt.plot(sprite_count, d2, label="Processing Time Pygame")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    # plt.show()
    plt.savefig("chart_stress_test_draw_moving_process_comparison.svg")
    plt.clf()


def chart_stress_test_collision_comparison():
    r1 = read_results("stress_test_collision_arcade.csv")
    r2 = read_results("stress_test_collision_arcade_spatial.csv")
    r3 = read_results("stress_test_collision_pygame_1_9_6.csv")

    sprite_count = [row[SPRITE_COUNT] for row in r1]
    d1 = [row[PROCESSING_TIME] for row in r1]
    d2 = [row[PROCESSING_TIME] for row in r2]
    d3 = [row[PROCESSING_TIME] for row in r3]

    # Plot our results
    plt.title("Colliding Sprites - Arcade vs Pygame")
    plt.plot(sprite_count, d1, label="Processing Time Arcade Normal")
    plt.plot(sprite_count, d2, label="Processing Time Arcade Spatial")
    plt.plot(sprite_count, d3, label="Processing Time Pygame")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    # plt.show()
    plt.savefig("chart_stress_test_collision_comparison.svg")
    plt.clf()


def main():
    chart_stress_test_draw_moving_pygame()
    chart_stress_test_draw_moving_arcade()
    chart_stress_test_draw_moving_draw_comparison()
    chart_stress_test_draw_moving_process_comparison()
    chart_stress_test_collision_comparison()


main()
