import os, sys

def main():
    if not os.path.exists('examples/thumbs'):
        os.makedirs('examples/thumbs')
        generate_thumbnails()
    else:
        print('Thumbnails already exist, skipping generation')


def generate_thumbnails():
    print('Generating thumbnails')

    if sys.platform == 'linux':
        command = 'mogrify'
    else:
        command = 'magick mogrify'

    os.chdir('examples')
    os.system(command + ' -resize 200x158 -extent 200x158 -background transparent -path thumbs *.png')
    # os.system(command + ' -resize 200x158 -extent 200x158 -background transparent -path thumbs *.gif')

if __name__ == '__main__':
    main()
