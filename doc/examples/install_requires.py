setup(
    ...
    install_requires=[
        'arcade',
    ],
    # If you have resources
    include_package_data=True,
    package_data={
        # Replace appname with the name of your complicated
        # Replace the value here with a list of files that contain
        #   your game's resources
        'appname': ['/images/*',],
    },
)
