import pathlib, os

from PIL import Image

def main():
    if not os.path.exists('examples/thumbs'):
        os.makedirs('examples/thumbs')
        generate_thumbnails()
    else:
        print('Thumbnails already exist, skipping generation')


def generate_thumbnails():
    print('Generating thumbnails')

    size = 200, 158

    for infile in pathlib.Path('.').glob('examples/*.png'):
        im = Image.open(infile)
        im.thumbnail(size)
        im.save('examples/thumbs/' + infile.name)


if __name__ == '__main__':
    main()
