#
# Justin A. Langley
# Student ID: 001036634
# 2022-03-22
#
def main():
    import cli.io as io
    import cli.prompts as prompts
    from app import App
    from core.hub import Hub

    prompts.display_welcome()

    # request data files from the user
    data_locations = ['../data/gps/', '../data/package/']
    gps_data_path, package_data_path = io.request_data_files(data_locations, '.csv')

    # preliminary data processing for building necessary objects
    graph, addresses = io.build_graph(path=gps_data_path)
    packages = io.build_packages(path=package_data_path, addresses=addresses)

    from WGUPS.cli.environment import cls
    cls()
    hub = Hub(addresses=addresses, graph=graph, packages=packages)

    # Initialize the app
    app = App(hub=hub)
    app.run()


if __name__ == '__main__':
    main()
