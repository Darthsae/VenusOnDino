import argparse, pstats

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="input file name")
    parser.add_argument("output", type=str, help="output file name")
    args = parser.parse_args()
    with open(args.output, "w") as f:
        stats = pstats.Stats(args.input, stream=f)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats()