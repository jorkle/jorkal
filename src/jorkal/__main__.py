from jorkal import main


def execute_jorkal():
    """Executes the initial entry point of Jorkal.

    This functionality exists to ensure that Jorkal still executes in certain scenarios (see below).

    Example: `python3 -m jorkal`
    """
    main.run()


if __name__ == "__main__":
    execute_jorkal()
