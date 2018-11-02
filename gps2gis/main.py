#!python3 -x
"""Driver for gps2gis.
Functions:
main -- main method
"""
import argparse
from gps2gis.dataset import Dataset


def main():
    parser = argparse.ArgumentParser(description='Convert gps log to GIS formats.')
    parser.add_argument('--delay', '-d', type=int, default=5, help='Minimum seconds to consider a stop. (default 5)')
    parser.add_argument('--geotype', '-g', choices=['multipoint', 'polygon'], default='multipoint', help='Type of output: "multipoint" or "polygon" (default "multipoint")')
    parser.add_argument('--format', '-f', choices=['shapefile'], default='shapefile', help='GIS Format: "shapefile" (default "shapefile")')
    parser.add_argument('--merge', '-m', action='store_true', help='Merge overlapping polygons (Only meaningful if output is set to polygon)')
    parser.add_argument('--output', '-o', required=True, help='Path to shapefile output folder')
    parser.add_argument('--stop', '-s', type=float, default=0.1, help='Maximum speed to consider as stopped (default 0.1)')
    parser.add_argument('input', nargs='*', help='Input file(s)')
    args = parser.parse_args()
    for input_file in args.input:
        d = Dataset(input_file)
        if args.format == 'shapefile':
            if args.geotype == 'multipoint':
                d.write_multipoint(args.output, args.stop, args.delay)
            elif args.geotype == 'polygon':
                d.write_polygon(args.output, args.stop, args.delay, args.merge)
            


if __name__ == "__main__":
    main()