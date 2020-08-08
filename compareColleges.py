import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-c1", "--college", help = "First College to compare")
ap.add_argument("-c2", "--compare", help = "Second College to compare")
ap.add_argument("-d", "--driver", help = "Path to Selenium Driver")

args = vars(ap.parse_args())
